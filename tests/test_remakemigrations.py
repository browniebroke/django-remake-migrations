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


class RemakeMigrationsTests(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        migrations_module_name1 = "migrations" + str(time.time()).replace(".", "") + "1"
        self.testapp_mig_dir = tmp_path / migrations_module_name1
        self.testapp_mig_dir.mkdir()

        migrations_module_name2 = "migrations" + str(time.time()).replace(".", "") + "2"
        self.testapp2_mig_dir = tmp_path / migrations_module_name2
        self.testapp2_mig_dir.mkdir()

        sys.path.insert(0, str(tmp_path))
        try:
            with override_settings(
                MIGRATION_MODULES={
                    "testapp": migrations_module_name1,
                    "testapp2": migrations_module_name2,
                }
            ):
                yield
        finally:
            sys.path.pop(0)

    def test_success_all_steps(self):
        (self.testapp_mig_dir / "__init__.py").touch()
        initial_0001 = self.testapp_mig_dir / "0001_initial.py"
        initial_0001.write_text(EMPTY_MIGRATION)
        migration_0002 = self.testapp_mig_dir / "0002_something.py"
        migration_0002.write_text(
            dedent(
                """\
                from django.db import migrations

                class Migration(migrations.Migration):
                    dependencies = [
                        ('testapp', '0001_initial'),
                        ('testapp2', '0001_initial'),
                    ]
                    operations = []
                """
            )
        )
        migration_0003 = self.testapp_mig_dir / "0003_other_thing.py"
        migration_0003.write_text(
            dedent(
                """\
                from django.db import migrations

                class Migration(migrations.Migration):
                    dependencies = [
                        ('testapp', '0002_something'),
                    ]
                    operations = []
                """
            )
        )

        (self.testapp2_mig_dir / "__init__.py").touch()
        initial_0001 = self.testapp2_mig_dir / "0001_initial.py"
        initial_0001.write_text(EMPTY_MIGRATION)

        out, err, returncode = run_command("remakemigrations")

        assert out == ""
        assert err == ""
        assert returncode == 0

        dir_files = sorted(os.listdir(self.testapp_mig_dir))
        today = datetime.today()
        initial_remade_name = f"0001_remaked_{today:%Y%m%d}_initial.py"
        assert dir_files == [
            initial_remade_name,
            "__init__.py",
        ]

        initial_remade = self.testapp_mig_dir / initial_remade_name
        content = initial_remade.read_text()

        assert "from django.db import migrations" in content
        assert "class Migration(migrations.Migration):" in content
        assert "initial = True" in content
        assert (
            "    dependencies = [\n"
            f"        ('testapp2', '0001_remaked_{today:%Y%m%d}_initial'),\n"
            "    ]\n" in content
        )
        assert (
            "replaces = [('testapp', '0001_initial'), "
            "('testapp', '0002_something'), "
            "('testapp', '0003_other_thing')]" in content
        )
