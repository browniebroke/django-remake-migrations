"""
These are the available settings.

All attributes prefixed ``REMAKE_MIGRATIONS_*`` can be overridden from your Django
project's settings module by defining a setting with the same name.

For instance, to run ``showmigrations`` and ``migrate`` after remaking,
add the following to your project settings:

.. code-block:: python

    REMAKE_MIGRATIONS_POST_COMMANDS = [
        ["showmigrations"],
        ["migrate"],
    ]
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from django.conf import settings as django_settings

# All attributes accessed with this prefix are possible to overwrite
# through django.conf.settings.
SETTINGS_PREFIX = "REMAKE_MIGRATIONS_"


@dataclass(frozen=True)
class AppSettings:
    """Access this instance as `django_remake_migrations.conf.app_settings`."""

    REMAKE_MIGRATIONS_FIRST_APPS: Sequence[str] = ()
    """The apps for which to make migrations first."""

    REMAKE_MIGRATIONS_LAST_APPS: Sequence[str] = ()
    """The apps for which to make migrations last."""

    REMAKE_MIGRATIONS_POST_COMMANDS: Sequence[Sequence[str]] = ()
    """Some commands with arguments to run after generating the new migration."""

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
