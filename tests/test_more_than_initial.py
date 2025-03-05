from __future__ import annotations

import os
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest
from django.test import TestCase, override_settings

from tests.utils import EMPTY_MIGRATION, run_command, setup_test_apps


def migrations_for_squash_app_a(app_a_mig_dir: Path) -> None:
    (app_a_mig_dir / "__init__.py").touch()
    initial_0001 = app_a_mig_dir / "0001_initial.py"
    initial_0001.write_text(EMPTY_MIGRATION)


def migrations_for_squash_app_b(app_b_mig_dir: Path) -> None:
    (app_b_mig_dir / "__init__.py").touch()
    initial_0001 = app_b_mig_dir / "0001_initial.py"
    initial_0001.write_text(EMPTY_MIGRATION)


class TestReplacesWarning(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        with setup_test_apps(
            tmp_path,
            "tests.more_than_initial.app_a",
            "tests.more_than_initial.app_b",
        ) as self.app_mig_dirs:
            yield

    def test_prints_replaces_warning(self):
        app_a_mig_dir = self.app_mig_dirs["app_a"]
        migrations_for_squash_app_a(app_a_mig_dir)
        app_b_mig_dir = self.app_mig_dirs["app_b"]
        migrations_for_squash_app_b(app_b_mig_dir)

        out, err, returncode = run_command("remakemigrations")

        assert (
            out == "Removing old migration files...\n"
            "Creating new migrations...\n"
            "Updating new migrations...\n"
            "All done!\n"
        )
        assert (
            err
            == "App app_a has more migrations than before... Replaces might be wrong!\n"
        )
        assert returncode == 0

        dir1_files = sorted(
            [file for file in os.listdir(app_a_mig_dir) if file != "__pycache__"]
        )
        today = datetime.today()
        initial_remade_name = f"0001_remaked_{today:%Y%m%d}.py"
        second_remade_name = f"0002_remaked_{today:%Y%m%d}.py"
        assert dir1_files == [
            initial_remade_name,
            second_remade_name,
            "__init__.py",
        ]

        dir2_files = sorted(
            [file for file in os.listdir(app_b_mig_dir) if file != "__pycache__"]
        )
        today = datetime.today()
        initial_remade_name = f"0001_remaked_{today:%Y%m%d}.py"
        assert dir2_files == [
            initial_remade_name,
            "__init__.py",
        ]

        initial_remade = app_a_mig_dir / initial_remade_name
        content_app_a_initial = initial_remade.read_text()
        second_remade = app_a_mig_dir / second_remade_name
        content_app_a_second = second_remade.read_text()

        assert "from django.db import migrations" in content_app_a_initial
        assert "class Migration(migrations.Migration):" in content_app_a_initial
        assert "initial = True" in content_app_a_initial
        assert "replaces = [('app_a', '0001_initial')]" not in content_app_a_initial
        assert "initial = True" in content_app_a_second
        assert "replaces = [('app_a', '0001_initial')]" in content_app_a_second


class TestReplacesAll(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        with setup_test_apps(
            tmp_path,
            "tests.more_than_initial.app_a",
            "tests.more_than_initial.app_b",
        ) as self.app_mig_dirs:
            yield

    @override_settings(REMAKE_MIGRATIONS_REPLACES_ALL=True)
    def test_replaces_all(self):
        app_a_mig_dir = self.app_mig_dirs["app_a"]
        migrations_for_squash_app_a(app_a_mig_dir)
        app_b_mig_dir = self.app_mig_dirs["app_b"]
        migrations_for_squash_app_b(app_b_mig_dir)

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
        second_remade_name = f"0002_remaked_{today:%Y%m%d}.py"
        initial_remade = app_a_mig_dir / initial_remade_name
        content_app_a_initial = initial_remade.read_text()
        second_remade = app_a_mig_dir / second_remade_name
        content_app_a_second = second_remade.read_text()

        assert "replaces = [('app_a', '0001_initial')]" in content_app_a_initial
        assert "initial = True" in content_app_a_second
        assert "replaces = [('app_a', '0001_initial')]" in content_app_a_second


class TestReplaceOtherApps(TestCase):
    @pytest.fixture(autouse=True)
    def tmp_path_fixture(self, tmp_path: Path) -> Generator[None, None, None]:
        with setup_test_apps(
            tmp_path,
            "tests.more_than_initial.app_a",
            "tests.more_than_initial.app_b",
        ) as self.app_mig_dirs:
            yield

    @override_settings(
        REMAKE_MIGRATIONS_REPLACES_ALL=True,
        REMAKE_MIGRATIONS_REPLACE_OTHER_APP={"app_a": ["app_b"]},
    )
    def test_replace_other_app(self):
        app_a_mig_dir = self.app_mig_dirs["app_a"]
        migrations_for_squash_app_a(app_a_mig_dir)
        app_b_mig_dir = self.app_mig_dirs["app_b"]
        migrations_for_squash_app_b(app_b_mig_dir)

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
        second_remade_name = f"0002_remaked_{today:%Y%m%d}.py"
        initial_remade = app_a_mig_dir / initial_remade_name
        content_app_a_initial = initial_remade.read_text()
        second_remade = app_a_mig_dir / second_remade_name
        content_app_a_second = second_remade.read_text()

        assert (
            "replaces = [('app_a', '0001_initial'), ('app_b', '0001_initial')]"
            in content_app_a_initial
        )
        assert "initial = True" in content_app_a_second
        assert (
            "replaces = [('app_a', '0001_initial'), ('app_b', '0001_initial')]"
            in content_app_a_second
        )
