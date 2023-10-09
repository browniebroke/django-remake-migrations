from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RemakeMigrationAppConfig(AppConfig):
    """App config for the remake migration app."""

    name = "remake_migrations"
    verbose_name = _("remake migrations")
