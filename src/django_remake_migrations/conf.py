"""
These are the available settings.

All attributes prefixed ``REMAKE_MIGRATIONS_*`` can be overridden from your Django
project's settings module by defining a setting with the same name.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings as django_settings

# All attributes accessed with this prefix are possible to overwrite
# through django.conf.settings.
SETTINGS_PREFIX = "REMAKE_MIGRATIONS_"


@dataclass(frozen=True)
class AppSettings:
    """
    Proxy class to encapsulate all the app settings.

    This instance should be accessed via the singleton
    ``django_remake_migrations.conf.app_settings``.

    You shouldn't have to set any of these yourself, the class checks a Django
    settings with the same name and use these if defined, defaulting to the
    values documented here.
    """

    REMAKE_MIGRATIONS_FIRST_APPS: Sequence[str] = ()
    """The apps for which to make migrations first."""

    REMAKE_MIGRATIONS_LAST_APPS: Sequence[str] = ()
    """The apps for which to make migrations last."""

    REMAKE_MIGRATIONS_POST_COMMANDS: Sequence[Sequence[str]] = ()
    """
    Django management commands to run after generating the new migration.

    Each command and its arguments should be specified as a list or tuple.
    For example, to integrate with django-linear-migrations:

    .. code-block:: python

        REMAKE_MIGRATIONS_POST_COMMANDS = [
            ["create_max_migration_files", "--recreate"],
        ]
    """

    REMAKE_MIGRATIONS_EXTENSIONS: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    """
    The database extensions to enable for each app.

    Keys are app labels and values are a list of the full import path
    of the extension classes:

    .. code-block:: python

        REMAKE_MIGRATIONS_EXTENSIONS = {
            "app1": ["django.contrib.postgres.operations.TrigramExtension"],
        }
    """

    def __getattribute__(self, __name: str) -> Any:
        """
        Check if a Django project settings should override the app default.

        In order to avoid returning any random properties of the django settings,
        we inspect the prefix firstly.
        """
        if __name.startswith(SETTINGS_PREFIX) and hasattr(django_settings, __name):
            return getattr(django_settings, __name)

        return super().__getattribute__(__name)


app_settings = AppSettings()
