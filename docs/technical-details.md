(technical-details)=

# Technical details

This command is a bit like the built-in [`squashmigrations` command](https://docs.djangoproject.com/en/stable/ref/django-admin/#squashmigrations), but on steroids. The `remakemigrations` command makes different trade-offs, and might not be suitable to all use cases, so it's important to understand the differences.

As explained earlier, the command performs the following steps:

1. Remove all existing 1st party migrations on disk, project wide.
2. Call Django's `makemigrations`.
3. Mark all new migrations as replacements of the ones deleted at step 1.

This results in an entirely new migration graph, completely free of the history of the project, as if the migrations where generated from scratch.

## Differences with `squashmigrations`

This is quite different from how `squashmigrations` works:

1. AFAIK, `squashmigrations` works on a single app at a time, while `remakemigrations` works on the whole project, thus simplifying the migration graph at the project level.
2. The number of operations is optimised to the minimum amount (see later).
3. `remakemigrations` does not try to be correct when calculating replacements.

### Migration graph

On a project with enough cross-apps dependencies, it can become arduous to run `squashmigrations`, if your migration graph has cycles. You need to run it for each app, in the right order.

### Operations

The built-in `squashmigrations` creates a new migration file containing all the operations from squashed migrations, in a single file. This reduces the number of migration files, but it doesn't simplify the migrations themselves, the number of operations is roughly the same.

If we add a model to an app, make some changes to it, and after a while remove it, we could optimise the migration by dropping all operations related to this model, but `squashmigrations` doesn't do that.

Django 4.1 introduced a new [`optimizemigrations` command](https://docs.djangoproject.com/en/stableref/django-admin/#optimizemigration) which sounds like it might be doing just this, but I never had a chance to use it.

### Correctness

The built-in `squanshmigrations` command, needs to be correct in all cases. It needs to produce new migrations that can work even if they are deployed to systems where not all migrations are applied yet. This is especially needed for pluggable Django apps, where the developer of the app (usually) doesn't have control of all the deployments.

This package does not attempt to cater for this use case and does NOT try to be correct in the replacements it sets. The only guarantees are that:

- all old migrations are marked as replaced **exactly once**.
- any remade migration replaces at least one of the old migrations.

As long as all the environments are fully migrated when you deploy the remade migrations, it shouldn't be a problem.
