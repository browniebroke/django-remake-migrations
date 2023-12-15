from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Generator

import pytest
from django.test import TestCase, override_settings

from tests.utils import EMPTY_MIGRATION, run_command


class TestSimpleCase(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        migration_modules = {}
        self.app_mig_dirs = {}
        for app_name in ["app1", "app2"]:
            mig_module_name = (
                "migrations" + str(time.time()).replace(".", "") + app_name
            )
            migration_modules[app_name] = mig_module_name
            self.app_mig_dirs[app_name] = tmp_path / mig_module_name
            self.app_mig_dirs[app_name].mkdir()

        sys.path.insert(0, str(tmp_path))
        try:
            with override_settings(
                INSTALLED_APPS=[
                    "tests.simple.app1",
                    "tests.simple.app2",
                    "django_remake_migrations",
                    "django.contrib.contenttypes",
                ],
                MIGRATION_MODULES=migration_modules,
            ):
                yield
        finally:
            sys.path.pop(0)

    def test_success_all_steps(self):
        app1_mig_dir = self.app_mig_dirs["app1"]
        (app1_mig_dir / "__init__.py").touch()
        initial_0001 = app1_mig_dir / "0001_initial.py"
        initial_0001.write_text(EMPTY_MIGRATION)
        migration_0002 = app1_mig_dir / "0002_something.py"
        migration_0002.write_text(
            dedent(
                """\
                from django.db import migrations

                class Migration(migrations.Migration):
                    dependencies = [
                        ('app1', '0001_initial'),
                        ('app2', '0001_initial'),
                    ]
                    operations = []
                """
            )
        )
        migration_0003 = app1_mig_dir / "0003_other_thing.py"
        migration_0003.write_text(
            dedent(
                """\
                from django.db import migrations

                class Migration(migrations.Migration):
                    dependencies = [
                        ('app1', '0002_something'),
                    ]
                    operations = []
                """
            )
        )

        app2_mig_dir = self.app_mig_dirs["app2"]
        (app2_mig_dir / "__init__.py").touch()
        initial_0001 = app2_mig_dir / "0001_initial.py"
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

        dir_files = sorted(os.listdir(app1_mig_dir))
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
        assert "initial = True" in content
        assert (
            "    dependencies = [\n"
            f"        ('app2', '0001_remaked_{today:%Y%m%d}'),\n"
            "    ]\n" in content
        )
        assert (
            "replaces = [('app1', '0001_initial'), "
            "('app1', '0002_something'), "
            "('app1', '0003_other_thing')]" in content
        )
