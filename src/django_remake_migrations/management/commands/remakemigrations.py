from __future__ import annotations

import datetime as dt
import sys
from argparse import ArgumentParser
from collections import defaultdict
from importlib import import_module
from pathlib import Path

from django.apps import AppConfig, apps
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand, call_command
from django.db.migrations import Migration
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.writer import MigrationWriter
from django.utils.module_loading import import_string

from django_remake_migrations.conf import app_settings


class CustomMigrationWriter(MigrationWriter):
    """
    Custom MigrationWriter which adds support for ``run_before``.

    There's a ticket and a PR in Django itself to add support for this.
    If that's merged in and released, we can remove this subclass when
    new versions of Django are installed.
    - https://code.djangoproject.com/ticket/36274
    - https://github.com/django/django/pull/19303.
    """

    def as_string(self) -> str:
        """Add run_before if available."""
        text = super().as_string()
        if self.migration.run_before:
            run_before_string = f"run_before = {self.migration.run_before}"
            text = text.replace(
                "class Migration(migrations.Migration):",
                f"class Migration(migrations.Migration):\n    {run_before_string}",
            )
        return text


class Command(BaseCommand):
    """
    Command to recreate all migrations from scratch.

    Mark new migrations as squashed.

    This might cause some inconsistencies, but should get you 99% there,
    after which we can fix issues manually.

    Can be validated by running:
    - showmigrations: should show the migration graph as expected
    - migrate: should not execute any migration
    - makemigrations: should not detect any differences
    """

    old_migrations: dict[str, list[tuple[str, str]]]
    renamed_files: dict[Path, Path]

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--keep-old-migrations",
            action="store_true",
            dest="keep_old_migrations",
            help="Don't delete old migrations files and keep them around.",
        )

    def handle(self, *args: str, keep_old_migrations: bool, **options: str) -> None:
        """Execute one step after another to avoid side effects between steps."""
        # Remove or rename old migration files
        self.handle_old_migrations(keep_old_migrations)
        # Recreate migrations
        self.make_migrations()
        # Update new files to be squashed of the old ones
        self.update_new_migrations()
        # Recreate old migrations
        if keep_old_migrations:
            self.restore_old_migrations()
        # Run other commands
        self.run_post_commands()
        self.log_info("All done!")

    def restore_old_migrations(self) -> None:
        """Restore old migrations after the command."""
        for old_name, new_name in self.renamed_files.items():
            Path(new_name).rename(old_name)

    def log_info(self, message: str) -> None:
        """Wrapper to help logging successes."""
        self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message: str) -> None:
        """Wrapper to help logging errors."""
        self.stderr.write(self.style.ERROR(message))

    def handle_old_migrations(self, keep_old_migrations: bool) -> None:
        """Remove all pre-existing migration files in first party apps."""
        action = "Backing up" if keep_old_migrations else "Removing"
        self.log_info(f"{action} old migration files...")
        loader = MigrationLoader(None, ignore_no_migrations=True)
        old_migrations = defaultdict(list)
        self.renamed_files = {}
        for (app_label, migration_name), _migration_obj in loader.graph.nodes.items():
            app_config = apps.get_app_config(app_label)
            if self._is_first_party(app_config):
                old_migrations[app_label].append((app_label, migration_name))
                rename = self.handle_old_migration_file(
                    app_label=app_label,
                    migration_name=migration_name,
                    keep_old_migrations=keep_old_migrations,
                )
                self.renamed_files.update(rename)
        self.old_migrations = dict(old_migrations)

    def make_migrations(self) -> None:
        """Recreate migrations from scratch with a unique name."""
        self.log_info("Creating new migrations...")
        name = f"remaked_{dt.date.today():%Y%m%d}"
        if first_apps := app_settings.REMAKE_MIGRATIONS_FIRST_APPS:
            self.log_info(f"First apps: {', '.join(first_apps)}...")
            call_command("makemigrations", "--name", name, *first_apps)

        if last_apps := app_settings.REMAKE_MIGRATIONS_LAST_APPS:
            apps_to_make = [
                app_config.label
                for app_config in apps.get_app_configs()
                if app_config.label not in last_apps
            ]
            self.log_info(f"Middle apps {', '.join(apps_to_make)}...")
            call_command("makemigrations", "--name", name, *apps_to_make)

            self.log_info(f"Last apps {', '.join(last_apps)}...")
            call_command("makemigrations", "--name", name, *last_apps)

        # Always run a final round, just in case
        call_command("makemigrations", "--name", name)

    @staticmethod
    def _is_first_party(app_config: AppConfig) -> bool:
        app_path = Path(app_config.path)
        return (
            "site-packages" not in app_path.parts
            and "dist-packages" not in app_path.parts
        )

    @staticmethod
    def handle_old_migration_file(
        app_label: str, migration_name: str, keep_old_migrations: bool
    ) -> dict[Path, Path]:
        """
        Removes or rename old migration file.

        Remove file from the disk for the specified migration
        or rename if we need to keep around old migrations.
        """
        app_migrations_module_name, _ = MigrationLoader.migrations_module(app_label)
        migration_module = import_module(
            f"{app_migrations_module_name}.{migration_name}"
        )
        migration_file = Path(migration_module.__file__)  # type: ignore[arg-type]
        if keep_old_migrations:
            new_name = migration_file.with_suffix(".py-backup")
            migration_file.rename(new_name)
            rename = {migration_file: new_name}
        else:
            migration_file.unlink()
            rename = {}
        # Invalidate the import cache to avoid loading the old migration
        sys.modules.pop(migration_module.__name__, None)
        return rename

    def update_new_migrations(self) -> None:
        """
        Update auto-generated migrations after Django re-created them.

        Does a lot of things:

        - Rename migration files to have a unique name. If they have the same name as
          an old one, Django may be confused with replaces or dependencies.
        - Update dependencies to use the new unique names.
        - Add the old migrations to the `replaces` attributes of the new migrations.
          This is to mark the new migrations as squashed, so they are not actually
          executed by Django, they are simply marked as already applied.
        """
        self.log_info("Updating new migrations...")
        # Sort old migrations
        sorted_old_migrations = self.sort_migrations_map(self.old_migrations)
        loader = MigrationLoader(None, ignore_no_migrations=True, load=False)
        # Load migrations from the disk
        loader.load_disk()
        # Build a map of new migrations key per app
        new_migrations = defaultdict(list)
        for (
            app_label,
            migration_name,
        ), _migration_obj in loader.disk_migrations.items():
            if app_label in sorted_old_migrations:
                new_migrations[app_label].append((app_label, migration_name))

        # Sort new migrations
        sorted_new_migrations = self.sort_migrations_map(dict(new_migrations))
        # Do the main work
        for app_label, new_migrations_list in sorted_new_migrations.items():
            new_migrations_count = len(new_migrations_list)
            old_migrations_list = sorted_old_migrations[app_label]
            old_migrations_count = len(old_migrations_list)

            # We should have more migrations before
            if (
                old_migrations_count < new_migrations_count
                and not app_settings.REMAKE_MIGRATIONS_REPLACES_ALL
            ):
                self.log_error(
                    f"App {app_label} has more migrations than before... "
                    "Replaces might be wrong!"
                )

            # Calculate how many migrations will be replaced by the first one
            first_replaces_count = old_migrations_count - new_migrations_count + 1
            # Rewrite migrations with: new name, updated dependencies & replaces
            for index, migration_key in enumerate(new_migrations_list):
                migration_obj = loader.disk_migrations[migration_key]

                if app_settings.REMAKE_MIGRATIONS_REPLACES_ALL:
                    replaces_list = set(old_migrations_list)
                    for (
                        other_app
                    ) in app_settings.REMAKE_MIGRATIONS_REPLACE_OTHER_APP.get(
                        app_label, []
                    ):
                        replaces_list.update(sorted_old_migrations[other_app])
                    migration_obj.replaces = sorted(replaces_list)
                    if index == 0:
                        self.add_needed_database_extensions(migration_obj)
                else:
                    if index == 0:
                        # The first migration will replace the N first ones
                        migration_obj.replaces = old_migrations_list[
                            :first_replaces_count
                        ]
                        self.add_needed_database_extensions(migration_obj)
                    else:
                        # Otherwise, we replace a single migration
                        replaced_migration = old_migrations_list[
                            first_replaces_count + index - 1
                        ]
                        migration_obj.replaces = [replaced_migration]

                if (
                    app_settings.REMAKE_MIGRATIONS_RUN_BEFORE
                    and index == 0
                    and app_label in app_settings.REMAKE_MIGRATIONS_RUN_BEFORE
                ):
                    migration_obj.run_before = (
                        app_settings.REMAKE_MIGRATIONS_RUN_BEFORE[app_label]
                    )

                migration_obj.initial = True
                # Rewrite back to the disk
                self.write_to_disk(migration_obj)

    @staticmethod
    def sort_migrations_map(
        migrations_map: dict[str, list[tuple[str, str]]],
    ) -> dict[str, list[tuple[str, str]]]:
        """Sort migrations and group them by app."""
        return {
            app_label: sorted(migrations_list)
            for app_label, migrations_list in migrations_map.items()
        }

    @staticmethod
    def add_needed_database_extensions(migration_obj: Migration) -> None:
        """Add DB extensions for the app to the migration file."""
        app_label = migration_obj.app_label
        extensions = app_settings.REMAKE_MIGRATIONS_EXTENSIONS.get(app_label)
        if not extensions:
            return

        if isinstance(extensions, str):  # type: ignore[unreachable]
            raise ImproperlyConfigured(
                "REMAKE_MIGRATIONS_EXTENSIONS values should be a list, not a string."
            )

        extension_objects = [import_string(ext)() for ext in extensions]
        migration_obj.operations = [*extension_objects, *migration_obj.operations]

    @staticmethod
    def write_to_disk(migration_obj: Migration) -> None:
        """Write the migration object to the disk."""
        writer = CustomMigrationWriter(migration_obj)
        with open(writer.path, "w", encoding="utf-8") as fh:
            fh.write(writer.as_string())

    def run_post_commands(self) -> None:
        """Run other management commands at the very end."""
        post_commands = app_settings.REMAKE_MIGRATIONS_POST_COMMANDS
        if not post_commands:
            return

        self.log_info("Running post-commands...")
        for command_with_args in post_commands:
            self.log_info(f"Running: {' '.join(command_with_args)}")
            call_command(*command_with_args)
