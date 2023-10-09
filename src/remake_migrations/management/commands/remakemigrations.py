from __future__ import annotations

import datetime as dt
import pickle
from collections import defaultdict
from pathlib import Path

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.management import BaseCommand, CommandParser, call_command
from django.db.migrations import Migration
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.writer import MigrationWriter


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

    graph_file = Path(settings.BASE_DIR) / "graph.pickle"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add the option to run a specific step of the process."""
        super().add_arguments(parser)
        parser.add_argument("--step", type=int, action="store")

    def handle(self, step: int, *args: str, **options: str) -> None:
        """Execute one step after another to avoid side effects between steps."""
        if step == 1:
            # First, make sure we have applied all migrations
            call_command("migrate")
            # Remove old migration files
            self.clear_old_migrations()
        if step == 2:
            call_command("makemigrations")
        if step == 3:
            # Update new files to be squashed of the old ones
            self.update_new_migrations()
            # Delete the graph file
            self.graph_file.unlink()

    @property
    def old_migrations(self) -> dict[str, list[str]]:
        """Load old migrations from a pickle file."""
        with self.graph_file.open("rb") as fh:
            return pickle.load(fh)  # noqa S301

    @old_migrations.setter
    def old_migrations(self, value: dict[str, list[str]]) -> None:
        """Save old migrations in a pickle file."""
        with self.graph_file.open("wb") as fh:
            pickle.dump(value, fh)

    def clear_old_migrations(self) -> None:
        """Remove all pre-existing migration files in first party apps."""
        loader = MigrationLoader(None, ignore_no_migrations=True)
        old_migrations = defaultdict(list)
        for (app_label, migration_name), _migration_obj in loader.graph.nodes.items():
            app_config = apps.get_app_config(app_label)
            if self._is_first_party(app_config):
                old_migrations[app_label].append((app_label, migration_name))
                self.remove_migration_file(app_label, migration_name)
        self.old_migrations = dict(old_migrations)

    @staticmethod
    def _is_first_party(app_config: AppConfig) -> bool:
        app_path = Path(app_config.path)
        return (
            "site-packages" not in app_path.parts
            and "dist-packages" not in app_path.parts
        )

    @staticmethod
    def remove_migration_file(app_label: str, migration_name: str) -> None:
        """Remove file from the disk for the specified migration."""
        app_config = apps.get_app_config(app_label)
        migration_file = Path(app_config.path) / "migrations" / f"{migration_name}.py"
        migration_file.unlink()

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
            if old_migrations_count < new_migrations_count:
                self.log_error(
                    f"App {app_label} has more migrations than before... "
                    "Replaces might be wrong!"
                )
            # Calculate how many migrations will be replaced by the first one
            first_replaces_count = old_migrations_count - new_migrations_count + 1
            # Rewrite migrations with: new name, updated dependencies & replaces
            for index, migration_key in enumerate(new_migrations_list):
                migration_obj = loader.disk_migrations[migration_key]
                if index == 0:
                    # The first migration will replace the N first ones
                    migration_obj.replaces = old_migrations_list[:first_replaces_count]
                else:
                    # Otherwise, we replace a single migration
                    replaced_migration = old_migrations_list[
                        first_replaces_count + index - 1
                    ]
                    migration_obj.replaces = [replaced_migration]
                # Give the migration a unique name
                # to avoid clashes with pre-existing ones
                auto_name = migration_obj.name
                migration_obj.name = self.make_unique_name(auto_name)
                # Also update dependencies
                migration_obj.dependencies = [
                    (al, self.make_unique_name(mn))
                    if al in sorted_new_migrations
                    and (al, mn) in sorted_new_migrations[al]
                    else (al, mn)
                    for al, mn in migration_obj.dependencies
                ]
                migration_obj.initial = True
                # Rewrite back to the disk
                self.write_to_disk(migration_obj)
                # Remove the auto-generated migration file
                self.remove_migration_file(app_label, auto_name)

    @staticmethod
    def sort_migrations_map(
        migrations_map: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        """Sort migrations and group them by app."""
        return {
            app_label: sorted(migrations_list)
            for app_label, migrations_list in migrations_map.items()
        }

    @staticmethod
    def write_to_disk(migration_obj: Migration) -> None:
        """Write the migration object to the disk."""
        writer = MigrationWriter(migration_obj)
        with open(writer.path, "w", encoding="utf-8") as fh:
            fh.write(writer.as_string())

    @staticmethod
    def make_unique_name(auto_name: str) -> str:
        """Generate an auto-generated unique migration name."""
        if auto_name == "__first__":
            return auto_name
        today = dt.date.today()
        number, *name_parts = auto_name.split("_")
        # Don't use 'squashed' in the name as Django tries to be clever
        # and treats the date as the latest number
        return "_".join([number, "remaked", f"{today:%Y%m%d}", *name_parts])

    def log_error(self, message: str) -> None:
        """Wrapper to help logging errors."""
        self.stderr.write(self.style.ERROR(message))
