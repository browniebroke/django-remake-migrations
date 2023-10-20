(installation)=

# Installation

The package is published on [PyPI](https://pypi.org/project/django-remake-migrations/) and can be installed with `pip` (or any equivalent):

```bash
pip install django-remake-migrations
```

Add the app to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "remake_migrations",
]
```

Verify that the management command is available:

```bash
python manage.py remakemigrations --help
```

Which should print the command help:

```text
usage: manage.py remakemigrations [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

options:
  -h, --help            show this help message and exit
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```

All good? See the next {ref}`section about usage <usage>` to see how to use it.
