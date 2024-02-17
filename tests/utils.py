from __future__ import annotations

import contextlib
import sys
import time
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import Generator

from django.core.management import call_command
from django.test import override_settings


def run_command(*args, **kwargs):
    out = StringIO()
    err = StringIO()
    return_code: int | str | None = 0
    try:
        call_command(*args, stdout=out, stderr=err, **kwargs)
    except SystemExit as exc:  # pragma: no cover
        return_code = exc.code
    return out.getvalue(), err.getvalue(), return_code


EMPTY_MIGRATION = dedent(
    """\
    from django.db import migrations
    class Migration(migrations.Migration):
        pass
    """
)


@contextlib.contextmanager
def setup_test_apps(
    tmp_path: Path, *apps_to_install: str
) -> Generator[dict[str, Path], None, None]:
    """
    Setup given apps for testing.

    - Install given test apps
    - Set their migration directories to be under the given `tmp_path`.
    """
    migration_modules = {}
    app_mig_dirs: dict[str, Path] = {}
    for app in apps_to_install:
        app_name = app.split(".")[-1]
        mig_module_name = "migrations" + str(time.time()).replace(".", "") + app_name
        migration_modules[app_name] = mig_module_name
        app_mig_dirs[app_name] = tmp_path / mig_module_name
        app_mig_dirs[app_name].mkdir()

    sys.path.insert(0, str(tmp_path))
    try:
        with override_settings(
            INSTALLED_APPS=[
                *apps_to_install,
                "django_remake_migrations",
                "django.contrib.contenttypes",
            ],
            MIGRATION_MODULES=migration_modules,
        ):
            yield app_mig_dirs
    finally:
        sys.path.pop(0)
