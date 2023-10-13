from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest
from django.test import TestCase, override_settings

from tests.utils import EMPTY_MIGRATION, run_command


class RemakeMigrationsTests(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path):
        migrations_module_name = "migrations" + str(time.time()).replace(".", "")
        self.migrations_dir = tmp_path / migrations_module_name
        self.migrations_dir.mkdir()
        sys.path.insert(0, str(tmp_path))
        try:
            with override_settings(
                MIGRATION_MODULES={"testapp": migrations_module_name}
            ):
                yield
        finally:
            sys.path.pop(0)

    def test_success_step_1(self):
        (self.migrations_dir / "__init__.py").touch()
        initial_0001 = self.migrations_dir / "0001_initial.py"
        initial_0001.write_text(EMPTY_MIGRATION)
        migration_0002 = self.migrations_dir / "0002_something.py"
        migration_0002.write_text(
            dedent(
                """\
            from django.db import migrations

            class Migration(migrations.Migration):
                dependencies = [
                    ('testapp', '0001_initial'),
                ]
                operations = []
            """
            )
        )

        out, err, returncode = run_command("remakemigrations", "--step", "1")

        assert out == ""
        assert err == ""
        assert returncode == 0

        assert not initial_0001.exists()
        assert not migration_0002.exists()

        graph_json = Path(__file__).parent / "graph.json"
        assert graph_json.exists()

    def test_success_step_2_and_3(self):
        (self.migrations_dir / "__init__.py").touch()
        graph_json = Path(__file__).parent / "graph.json"
        graph_json.write_text(
            json.dumps(
                {
                    "testapp": [
                        ["testapp", "0001_initial"],
                        ["testapp", "0002_something"],
                        ["testapp", "0003_other_thing"],
                    ]
                }
            )
        )

        out, err, returncode = run_command("remakemigrations", "--step", "2")

        assert out == ""
        assert err == ""
        assert returncode == 0

        dir_files = sorted(os.listdir(self.migrations_dir))
        assert dir_files == [
            "0001_initial.py",
            "__init__.py",
        ]

        initial_0001 = self.migrations_dir / "0001_initial.py"
        content = initial_0001.read_text()

        assert "from django.db import migrations, models" in content
        assert "class Migration(migrations.Migration):" in content
        assert "initial = True" in content
        assert "replaces = " not in content

        out, err, returncode = run_command("remakemigrations", "--step", "3")

        assert out == ""
        assert err == ""
        assert returncode == 0

        dir_files = sorted(os.listdir(self.migrations_dir))
        today = datetime.today()
        initial_remade_name = f"0001_remaked_{today:%Y%m%d}_initial.py"
        assert dir_files == [
            initial_remade_name,
            "__init__.py",
        ]

        initial_remade = self.migrations_dir / initial_remade_name
        content = initial_remade.read_text()

        assert "from django.db import migrations, models" in content
        assert "class Migration(migrations.Migration):" in content
        assert "initial = True" in content
        assert (
            "replaces = [['testapp', '0001_initial'], "
            "['testapp', '0002_something'], "
            "['testapp', '0003_other_thing']]" in content
        )
