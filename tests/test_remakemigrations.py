from __future__ import annotations

import sys
import time
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
