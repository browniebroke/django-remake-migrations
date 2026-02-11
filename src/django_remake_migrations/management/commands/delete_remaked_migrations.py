from __future__ import annotations

import types
from argparse import ArgumentParser
from collections import defaultdict
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from django.apps import AppConfig, apps
from django.core.management import BaseCommand
from django.db.migrations import Migration
from django.db.migrations.exceptions import BadMigrationError
from django.db.migrations.loader import MigrationLoader

from django_remake_migrations.management.migration_writer import CustomMigrationWriter


class Command(BaseCommand):
    """
    Command to clear the `replaces` attribute on remaked migrations.

    This command should only be run after all environments have applied
    the remaked migrations. The `replaces` attribute is used by Django
    to map old migrations to the new remaked ones, but once all environments
    are migrated, this attribute is no longer needed.

    The command will:
    - Find all migration files containing '_remaked_' in their name
    - Remove only the `replaces` attribute from each file
    - Keep all other attributes (like `initial = True`) intact
    - Only process first-party apps (not site-packages/dist-packages)
    - Optionally delete the replaced migrations (--remove-replaced)

    You need to ensure that the remaked migrations are fully rolled out everywhere
    before deploying the result of this command.
    """

    help = (
        "Remove the 'replaces' attribute from remaked migrations after they've been "
        "fully deployed to all environments. Optionally also deletes "
        "the replaced migrations."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Show what would be done without making any changes.",
        )
        parser.add_argument(
            "--app-label",
            dest="app_label",
            help="Only process migrations for the specified app.",
        )
        parser.add_argument(
            "--remove-replaced",
            dest="remove_replaced",
            action="store_true",
            help="Remove the files containing the replaced migrations",
        )

    def handle(
        self,
        *args: str,
        dry_run: bool = False,
        app_label: str | None = None,
        remove_replaced: bool = False,
        **options: Any,
    ) -> None:
        """Command entry point."""
        # Find all remaked migrations
        remaked_migrations = self.find_remaked_migrations(app_label)

        if not remaked_migrations:
            self.log_info("No remaked migrations found.")
            return

        # Display what will be done
        total_count = sum(len(migrations) for migrations in remaked_migrations.values())
        self.stdout.write(
            f"Found {total_count} remaked migration(s) in "
            f"{len(remaked_migrations)} app(s)"
        )

        if dry_run:
            self.log_info("\nDry run - no files will be modified.\n")

        # Process each migration
        success_count = 0
        deleted_migrations: set[tuple[str, str]] = set()

        for app, migrations in sorted(remaked_migrations.items()):
            for _, migration_name, file_path, migration_module in migrations:
                remove_result, replaces = self.remove_replaces_from_file(
                    file_path,
                    migration_module,
                    dry_run=dry_run,
                    remove_replaced=remove_replaced,
                )

                if remove_result:
                    if dry_run:
                        self.stdout.write(
                            f"Would remove replaces from: {app}.{migration_name}"
                        )
                        if remove_replaced:
                            deleted_migrations.update(replaces)
                            for to_remove in replaces:
                                self.stdout.write(
                                    f"  - would delete migration "
                                    f"{to_remove[1]!r} from app {to_remove[0]!r}"
                                )
                    else:
                        self.log_info(f"Removed replaces from: {app}.{migration_name}")
                        if remove_replaced:
                            deleted_migrations.update(replaces)
                            for to_remove in replaces:
                                self.stdout.write(
                                    f"  - deleted migration "
                                    f"{to_remove[1]!r} from app {to_remove[0]!r}"
                                )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No replaces attribute found in: {app}.{migration_name}"
                        )
                    )

        # Final summary
        self.stdout.write("")
        if remove_replaced and dry_run:
            self.log_info(
                f"Dry run complete. Would have processed {success_count} migration(s) "
                f"and deleted {len(deleted_migrations)} migration(s)."
            )
        elif remove_replaced:
            self.log_info(
                f"Successfully processed {success_count} migration(s) "
                f"and deleted {len(deleted_migrations)} migration(s)."
            )
        elif dry_run:
            self.log_info(
                f"Dry run complete. Would have processed {success_count} migration(s)."
            )
        else:
            self.log_info(f"Successfully processed {success_count} migration(s).")

    def find_remaked_migrations(
        self, app_label: str | None = None
    ) -> dict[str, list[tuple[str, str, Path, types.ModuleType]]]:
        """
        Find all remaked migration files.

        Returns:
            Dictionary mapping app_label to list of
            (app_label, migration_name, file_path) tuples

        """
        loader = MigrationLoader(None, ignore_no_migrations=True)
        remaked_migrations = defaultdict(list)

        for (
            app_label_iter,
            migration_name,
        ), _migration_obj in loader.graph.nodes.items():
            # Filter by app_label if specified
            if app_label and app_label_iter != app_label:
                continue

            # Check if this is a first-party app
            app_config = apps.get_app_config(app_label_iter)
            if not self._is_first_party(app_config):
                continue

            # Check if migration name contains "_remaked_"
            if "_remaked_" not in migration_name:
                continue

            # Get the file path
            app_migrations_module_name, _ = MigrationLoader.migrations_module(
                app_label_iter
            )
            migration_module = import_module(
                f"{app_migrations_module_name}.{migration_name}"
            )
            migration_file = Path(migration_module.__file__)  # type: ignore[arg-type]
            remaked_migrations[app_label_iter].append(
                (app_label_iter, migration_name, migration_file, migration_module)
            )

        return dict(remaked_migrations)

    def remove_replaces_from_file(
        self,
        file_path: Path,
        migration_module: ModuleType,
        dry_run: bool = False,
        remove_replaced: bool = False,
    ) -> tuple[bool, list[tuple[str, str]]]:
        """
        Remove the replaces attribute from a migration file.

        Returns:
            True if replaces was found and removed, False otherwise

        """
        if not hasattr(migration_module, "Migration"):
            raise BadMigrationError(
                f"Migration {migration_module} has no Migration class"
            )
        migration: Migration = migration_module.Migration

        if not migration.replaces:
            return False, migration.replaces or []

        if dry_run:
            return True, migration.replaces or []

        replaces = list(migration.replaces or [])

        migration.replaces = None

        writer = CustomMigrationWriter(migration)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(writer.as_string())

        removed = replaces
        if remove_replaced:
            removed = []
            for app_label, migration_name in replaces:
                app_migrations_module_name, _ = MigrationLoader.migrations_module(
                    app_label
                )
                try:
                    migration_module = import_module(
                        f"{app_migrations_module_name}.{migration_name}"
                    )
                except ModuleNotFoundError:  # already is deleted
                    continue
                migration_file = Path(migration_module.__file__)  # type: ignore[arg-type]
                if migration_file.exists():
                    migration_file.unlink()
                    removed.append((app_label, migration_name))

        return True, removed

    @staticmethod
    def _is_first_party(app_config: AppConfig) -> bool:
        """Check if an app is first-party (not from site-packages)."""
        app_path = Path(app_config.path)
        return (
            "site-packages" not in app_path.parts
            and "dist-packages" not in app_path.parts
        )

    def log_info(self, message: str) -> None:
        """Wrapper to help logging successes."""
        self.stdout.write(self.style.SUCCESS(message))
