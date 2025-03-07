(usage)=

# Usage

Assuming that you've followed the {ref}`installations steps <installation>`, you should now have a [management command](https://docs.djangoproject.com/en/stable/ref/django-admin/) called `remakemigrations` available.

## Before starting

Before running the command, you need to make sure that your database is fully up-to-date with all the migration files present on disk. This is true for your development machine, but also for your staging/production environments.

In practical terms, that means that nothing is created when running `makemigrations` and that nothing happens when you run `migrate`:

```bash
python manage.py migrate
```

## Running the command

```{caution}
This command performs some destructive operations on your project: it will remove all migration files on disk.

Make sure all your migrations files are committed in source control before running it!
```

With that warning out of the way, you can run it with:

```bash
python manage.py remakemigrations
```

If you want to keep the old migration files around, you can use the option `--keep-old-migrations`:

```bash
python manage.py remakemigrations --keep-old-migrations
```

## What does it do?

At a high level, it does the following:

1. Remove all 1st party migration files from your project.
2. Call `makemigrations` to recreate all migrations as if you were starting from scratch.
3. Mark all new migrations as replacements of the ones deleted at step 1.

The 3rd step ensures that no migrations are reapplied to the various environments where the code is deployed.

These replacements aren't technically correct, but as long as all your environments are fully migrated, it shouldn't be a problem.

Want to know more about how it works? Read the {ref}`technical details page <technical-details>`.
