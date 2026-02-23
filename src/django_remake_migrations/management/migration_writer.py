from __future__ import annotations

from django.db.migrations.writer import MigrationWriter


class CustomMigrationWriter(MigrationWriter):
    """
    Custom MigrationWriter which adds support for ``run_before``.

    There's a ticket and a PR in Django itself to add support for this.
    If that's merged in and released, we can remove this subclass when
    new versions of Django are installed.
    - https://code.djangoproject.com/ticket/36274
    - https://github.com/django/django/pull/19303.
    """

    def as_string(self) -> str:
        """Add run_before if available."""
        text = super().as_string()
        if self.migration.run_before:
            run_before_string = f"run_before = {self.migration.run_before}"
            text = text.replace(
                "class Migration(migrations.Migration):",
                f"class Migration(migrations.Migration):\n    {run_before_string}",
            )
        return text
