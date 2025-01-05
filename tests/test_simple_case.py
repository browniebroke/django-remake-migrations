from __future__ import annotations

import os
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest
from django.test import TestCase

from tests.utils import EMPTY_MIGRATION, run_command, setup_test_apps


class TestSimpleCase(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        with setup_test_apps(
            tmp_path,
            "tests.simple.app1",
            "tests.simple.app2",
        ) as self.app_mig_dirs:
            yield

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

        dir_files = sorted(
            [file for file in os.listdir(app1_mig_dir) if file != "__pycache__"]
        )
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
