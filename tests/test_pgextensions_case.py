from __future__ import annotations

import os
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from tests.utils import EMPTY_MIGRATION, run_command, setup_test_apps


class TestSimpleCase(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        with setup_test_apps(
            tmp_path,
            "tests.pgextensions.app1",
        ) as self.app_mig_dirs:
            yield

    @override_settings(
        REMAKE_MIGRATIONS_EXTENSIONS={
            "app1": ["django.contrib.postgres.operations.TrigramExtension"]
        }
    )
    def test_extensions_added_to_first_app_migration(self):
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()
        initial_0001 = app1_mig_dir / "0001_initial.py"
        initial_0001.write_text(EMPTY_MIGRATION)

        out, err, returncode = run_command("remakemigrations")

        assert (
            out == "Removing old migration files...\n"
            "Creating new migrations...\n"
            "Updating new migrations...\n"
            "All done!\n"
        )
        assert err == ""
        assert returncode == 0

        dir_files = [
            it for it in sorted(os.listdir(app1_mig_dir)) if it != "__pycache__"
        ]
        today = datetime.today()
        initial_remade_name = f"0001_remaked_{today:%Y%m%d}.py"
        assert dir_files == [
            initial_remade_name,
            "__init__.py",
        ]

        initial_remade = app1_mig_dir / initial_remade_name
        content = initial_remade.read_text()

        assert "from django.db import migrations" in content
        assert "class Migration(migrations.Migration):" in content
        assert "import django.contrib.postgres.operations" in content
        assert (
            "    operations = [\n"
            "        django.contrib.postgres.operations.TrigramExtension(\n"
            "        )," in content
        )

    @override_settings(REMAKE_MIGRATIONS_EXTENSIONS={"app1": "TrigramExtension"})
    def test_improperly_configured(self):
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()
        initial_0001 = app1_mig_dir / "0001_initial.py"
        initial_0001.write_text(EMPTY_MIGRATION)

        with self.assertRaises(
            ImproperlyConfigured,
            msg="REMAKE_MIGRATIONS_EXTENSIONS values should be a list, not a string.",
        ):
            run_command("remakemigrations")
