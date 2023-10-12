from __future__ import annotations

from io import StringIO
from textwrap import dedent

from django.core.management import call_command


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
