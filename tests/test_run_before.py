from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest
from django.test import TestCase, override_settings

from tests.test_simple_case import (
    migrations_for_squash_app1,
    migrations_for_squash_app2,
)
from tests.utils import run_command, setup_test_apps


class TestRunBefore(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        with setup_test_apps(
            tmp_path,
            "tests.simple.app1",
            "tests.simple.app2",
        ) as self.app_mig_dirs:
            yield

    @override_settings(
        REMAKE_MIGRATIONS_RUN_BEFORE={"app1": [("oauth2_provider", "0001_initial")]},
    )
    def test_run_before(self):
        app1_mig_dir = self.app_mig_dirs["app1"]
        migrations_for_squash_app1(app1_mig_dir)
        app2_mig_dir = self.app_mig_dirs["app2"]
        migrations_for_squash_app2(app2_mig_dir)

        out, err, returncode = run_command("remakemigrations")

        assert (
            out == "Removing old migration files...\n"
            "Creating new migrations...\n"
            "Updating new migrations...\n"
            "All done!\n"
        )
        assert err == ""
        assert returncode == 0

        today = datetime.today()
        initial_remade_name = f"0001_remaked_{today:%Y%m%d}.py"

        initial_remade = app1_mig_dir / initial_remade_name
        content = initial_remade.read_text()
        print(content)

        assert "run_before = [('oauth2_provider', '0001_initial')]" in content
