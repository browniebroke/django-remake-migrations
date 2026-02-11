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

    You need to ensure that the remaked migrations are fully rolled out everywhere
    before deploying the result of this command.
    """

    help = (
        "Remove the 'replaces' attribute from remaked migrations after they've been "
        "fully deployed to all environments."
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

    def handle(
        self,
        *args: str,
        dry_run: bool = False,
        app_label: str | None = None,
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

        for app, migrations in sorted(remaked_migrations.items()):
            for _, migration_name, file_path, migration_module in migrations:
                if self.remove_replaces_from_file(file_path, migration_module, dry_run):
                    if dry_run:
                        self.stdout.write(
                            f"Would remove replaces from: {app}.{migration_name}"
                        )
                    else:
                        self.log_info(f"Removed replaces from: {app}.{migration_name}")
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No replaces attribute found in: {app}.{migration_name}"
                        )
                    )

        # Final summary
        self.stdout.write("")
        if dry_run:
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
        self, file_path: Path, migration_module: ModuleType, dry_run: bool = False
    ) -> bool:
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
            return False

        if dry_run:
            return True

        migration.replaces = None

        writer = CustomMigrationWriter(migration)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(writer.as_string())

        return True

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
