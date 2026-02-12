from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest
from django.test import TestCase

from tests.utils import run_command, setup_test_apps


def create_old_migration(mig_dir: Path, name: str) -> Path:
    """Helper to create an old migration file."""
    filename = f"{name}.py"
    file_path = mig_dir / filename
    content = dedent("""\
        from django.db import migrations


        class Migration(migrations.Migration):
            initial = True

            dependencies = []

            operations = []
    """)
    file_path.write_text(content)
    return file_path


def create_remaked_migration(
    mig_dir: Path,
    name: str,
    has_replaces: bool = True,
    multi_line_replaces: bool = False,
) -> Path:
    """Helper to create a remaked migration file."""
    filename = f"{name}_remaked_{datetime.today():%Y%m%d}.py"
    file_path = mig_dir / filename

    if not has_replaces:
        content = dedent("""\
            from django.db import migrations


            class Migration(migrations.Migration):
                initial = True

                dependencies = []

                operations = []
        """)
    elif multi_line_replaces:
        content = dedent("""\
            from django.db import migrations


            class Migration(migrations.Migration):
                initial = True

                dependencies = []

                replaces = [
                    ('app1', '0001_old'),
                    ('app1', '0002_old'),
                ]

                operations = []
        """)
    else:
        content = dedent("""\
            from django.db import migrations


            class Migration(migrations.Migration):
                initial = True

                dependencies = []

                replaces = [('app1', '0001_old'), ('app1', '0002_old')]

                operations = []
        """)

    file_path.write_text(content)
    return file_path


class TestDeleteRemakedMigrations(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        with setup_test_apps(
            tmp_path,
            "tests.delete.app1",
            "tests.delete.app2",
        ) as self.app_mig_dirs:
            yield

    def test_basic_case(self):
        """Test removing replaces from a single remaked migration."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        mig_file = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)

        out, err, returncode = run_command("delete_remaked_migrations")

        assert returncode == 0
        assert "Successfully processed 1 migration(s)" in out
        assert err == ""

        # Verify replaces was removed
        content = mig_file.read_text()
        assert "replaces" not in content
        assert "initial = True" in content  # Should still be present
        assert "operations = [\n    ]" in content  # Other content intact
        assert "class Migration(migrations.Migration):" in content

    def test_multiple_apps(self):
        """Test processing multiple apps with remaked migrations."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        app2_mig_dir = self.app_mig_dirs["app2"]
        (app1_mig_dir / "__init__.py").touch()
        (app2_mig_dir / "__init__.py").touch()

        mig1 = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        mig2 = create_remaked_migration(app2_mig_dir, "0001", has_replaces=True)

        out, err, returncode = run_command("delete_remaked_migrations")

        assert returncode == 0
        assert "Found 2 remaked migration(s) in 2 app(s)" in out
        assert "Successfully processed 2 migration(s)" in out
        assert err == ""

        # Both files should be modified
        assert "replaces" not in mig1.read_text()
        assert "replaces" not in mig2.read_text()
        assert "initial = True" in mig1.read_text()
        assert "initial = True" in mig2.read_text()

    def test_dry_run(self):
        """Test --dry-run doesn't modify files."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        mig_file = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        original_content = mig_file.read_text()

        out, err, returncode = run_command("delete_remaked_migrations", dry_run=True)

        assert returncode == 0
        assert "Dry run" in out
        assert "Would remove replaces from" in out
        assert "Would have processed 1 migration(s)" in out
        assert err == ""

        # Verify file wasn't modified
        assert mig_file.read_text() == original_content
        assert "replaces" in mig_file.read_text()

    def test_app_label_filter(self):
        """Test --app-label filters correctly."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        app2_mig_dir = self.app_mig_dirs["app2"]
        (app1_mig_dir / "__init__.py").touch()
        (app2_mig_dir / "__init__.py").touch()

        mig1 = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        mig2 = create_remaked_migration(app2_mig_dir, "0001", has_replaces=True)

        out, err, returncode = run_command(
            "delete_remaked_migrations", app_label="app1"
        )

        assert returncode == 0
        assert "Found 1 remaked migration(s) in 1 app(s)" in out
        assert "Successfully processed 1 migration(s)" in out
        assert err == ""

        # Only app1 should be modified
        assert "replaces" not in mig1.read_text()
        assert "replaces" in mig2.read_text()

    def test_no_remaked_migrations(self):
        """Test behavior when no remaked migrations exist."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        # Create a regular migration (not remaked)
        regular_mig = app1_mig_dir / "0001_initial.py"
        regular_mig.write_text(
            dedent(
                """\
            from django.db import migrations

            class Migration(migrations.Migration):
                operations = []
        """
            )
        )

        out, err, returncode = run_command("delete_remaked_migrations")

        assert returncode == 0
        assert "No remaked migrations found" in out
        assert err == ""

    def test_no_replaces_attribute(self):
        """Test handling of remaked migration without replaces."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        mig_file = create_remaked_migration(app1_mig_dir, "0001", has_replaces=False)

        out, err, returncode = run_command("delete_remaked_migrations")

        assert returncode == 0
        assert "No replaces attribute found in: app1.0001_remaked_" in out
        assert err == ""

        # File should be unchanged
        content = mig_file.read_text()
        assert "replaces" not in content
        assert "initial = True" in content

    def test_multi_line_replaces(self):
        """Test handling of multi-line replaces attribute."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        mig_file = create_remaked_migration(
            app1_mig_dir, "0001", has_replaces=True, multi_line_replaces=True
        )

        # Verify the multi-line format is present
        original_content = mig_file.read_text()
        assert "replaces = [\n" in original_content
        assert "('app1', '0001_old')" in original_content

        out, err, returncode = run_command("delete_remaked_migrations")

        assert returncode == 0
        assert "Successfully processed 1 migration(s)" in out
        assert err == ""

        # Verify all replaces lines were removed
        content = mig_file.read_text()
        assert "replaces" not in content
        assert "0001_old" not in content
        assert "0002_old" not in content
        assert "initial = True" in content
        assert "operations = [\n    ]" in content

    def test_multiple_migrations_same_app(self):
        """Test handling multiple remaked migrations in the same app."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        # Create two remaked migrations with different names
        # We need to use a different date format to ensure unique names
        mig1 = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        mig2 = create_remaked_migration(app1_mig_dir, "0002", has_replaces=True)

        out, err, returncode = run_command("delete_remaked_migrations")

        assert returncode == 0
        # Both migrations should be processed
        assert "Found 2 remaked migration(s) in 1 app(s)" in out
        assert "Successfully processed 2 migration(s)" in out
        assert err == ""

        # Both files should be modified
        assert "replaces" not in mig1.read_text()
        assert "replaces" not in mig2.read_text()

    def test_mixed_remaked_and_regular_migrations(self):
        """Test that only remaked migrations are processed."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        # Create one remaked and one regular migration
        remaked_mig = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        regular_mig = app1_mig_dir / "0002_regular.py"
        regular_content = dedent(
            """\
            from django.db import migrations

            class Migration(migrations.Migration):
                replaces = [('app1', '0000_initial')]
                operations = []
        """
        )
        regular_mig.write_text(regular_content)

        out, err, returncode = run_command("delete_remaked_migrations")

        assert returncode == 0
        assert "Successfully processed 1 migration(s)" in out
        assert err == ""

        # Only remaked migration should be modified
        assert "replaces" not in remaked_mig.read_text()
        assert "replaces" in regular_mig.read_text()  # Regular migration untouched

    def test_remove_replaced(self):
        """Test removing replaces with deleting replacede migrations."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        mig_file = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        old_file_01 = create_old_migration(app1_mig_dir, "0001_old")
        old_file_02 = create_old_migration(app1_mig_dir, "0002_old")

        out, err, returncode = run_command(
            "delete_remaked_migrations", remove_replaced=True
        )

        assert returncode == 0
        assert "Successfully processed 1 migration(s) and deleted 2 migration(s)" in out
        assert err == ""

        # Verify replaces was removed
        content = mig_file.read_text()
        assert "replaces" not in content
        assert "initial = True" in content  # Should still be present
        assert "operations = [\n    ]" in content  # Other content intact
        assert "class Migration(migrations.Migration):" in content

        assert old_file_01.exists() is False
        assert old_file_02.exists() is False

    def test_remove_replaced_dry_run(self):
        """Test dry-run replaces with deleting replacede migrations."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        mig_file = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        old_file_01 = create_old_migration(app1_mig_dir, "0001_old")
        old_file_02 = create_old_migration(app1_mig_dir, "0002_old")

        out, err, returncode = run_command(
            "delete_remaked_migrations", remove_replaced=True, dry_run=True
        )

        assert returncode == 0
        assert (
            "Dry run complete. Would have processed 1 "
            "migration(s) and deleted 2 migration(s)" in out
        )
        assert err == ""

        # Verify replaces was removed
        content = mig_file.read_text()
        assert "replaces" in content

        assert old_file_01.exists() is True
        assert old_file_02.exists() is True

    def test_remove_replaced_missing(self):
        """Test removing replaces with deleting replacede migrations."""
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()

        mig_file = create_remaked_migration(app1_mig_dir, "0001", has_replaces=True)
        old_file_01 = create_old_migration(app1_mig_dir, "0001_old")

        out, err, returncode = run_command(
            "delete_remaked_migrations", remove_replaced=True
        )

        assert returncode == 0
        assert "Successfully processed 1 migration(s) and deleted 1 migration(s)" in out
        assert err == ""

        # Verify replaces was removed
        content = mig_file.read_text()
        assert "replaces" not in content
        assert "initial = True" in content  # Should still be present
        assert "operations = [\n    ]" in content  # Other content intact
        assert "class Migration(migrations.Migration):" in content

        assert old_file_01.exists() is False
