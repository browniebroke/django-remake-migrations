# Django remake migrations

<p align="center">
  <a href="https://github.com/browniebroke/django-remake-migrations/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/browniebroke/django-remake-migrations/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://django-remake-migrations.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/django-remake-migrations.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/browniebroke/django-remake-migrations">
    <img src="https://img.shields.io/codecov/c/github/browniebroke/django-remake-migrations.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" alt="Poetry">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/django-remake-migrations/">
    <img src="https://img.shields.io/pypi/v/django-remake-migrations.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/django-remake-migrations.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/django-remake-migrations.svg?style=flat-square" alt="License">
</p>

---

**Documentation**: <a href="https://django-remake-migrations.readthedocs.io" target="_blank">https://django-remake-migrations.readthedocs.io</a>

**Source Code**: <a href="https://github.com/browniebroke/django-remake-migrations" target="_blank">https://github.com/browniebroke/django-remake-migrations </a>

---

A Django admin command to recreate all migrations in a project. Like a `squashmigrations` command on steroids.

## The problem

The built-in `squashmigrations` command is great, but it has some limitations:

- **It only works on a single app at a time**, which means that you need to run it for each app in your project. On a project with enough cross-apps dependencies, it quickly becomes impossible to run.
- **It doesn't optimise the operations**, it only reduces the number of migration files. That being said, Django 4.1 introduced a new [`optimizemigrations` command](https://docs.djangoproject.com/en/stable/ref/django-admin/#optimizemigration) which sounds like it might be doing just this.

This command aims at solving this problem, by recreating all the migration files in the whole project, from scratch, and mark them as applied by using the `replaces` attribute.

It makes an important trade-off though: it does NOT try to be correct when setting the `replaces` attribute. The only guarantees are that:

- all old migrations are marked as replaced **once**.
- all new migrations replace at least one of the old migrations

This is OK to make this trade-off as long as all your environments are fully migrated when you deploy the remade migrations.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://browniebroke.com/"><img src="https://avatars.githubusercontent.com/u/861044?v=4?s=80" width="80px;" alt="Bruno Alla"/><br /><sub><b>Bruno Alla</b></sub></a><br /><a href="https://github.com/browniebroke/django-remake-migrations/commits?author=browniebroke" title="Code">💻</a> <a href="#ideas-browniebroke" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/browniebroke/django-remake-migrations/commits?author=browniebroke" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DmytroLitvinov"><img src="https://avatars.githubusercontent.com/u/16066485?v=4?s=80" width="80px;" alt="Dmytro Litvinov"/><br /><sub><b>Dmytro Litvinov</b></sub></a><br /><a href="https://github.com/browniebroke/django-remake-migrations/commits?author=DmytroLitvinov" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

This package was created with
[Copier](https://copier.readthedocs.io/) and the
[browniebroke/pypackage-template](https://github.com/browniebroke/pypackage-template)
project template.
