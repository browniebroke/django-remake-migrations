# Changelog

## v2.8.0 (2025-09-18)

### Features

- Add support for python 3.14 ([`b5afaa7`](https://github.com/browniebroke/django-remake-migrations/commit/b5afaa732fe7086294acf9a8648c4c20db851f5d))
- Drop support for python 3.9 ([`435b8b5`](https://github.com/browniebroke/django-remake-migrations/commit/435b8b5ef80c31355cc2a9b47f331f2b15822d05))

## v2.7.1 (2025-08-25)

### Bug fixes

- Use spdx expression for license ([`6eaa6a5`](https://github.com/browniebroke/django-remake-migrations/commit/6eaa6a54c9b54c40e2f5741835d1a1572c5da45f))

### Documentation

- Remove duplicated h1 header ([`ecf560f`](https://github.com/browniebroke/django-remake-migrations/commit/ecf560f4ba7507b5375ab14fc351db5643668aab))
- Move toc to the bottom of index page ([`0191812`](https://github.com/browniebroke/django-remake-migrations/commit/01918125d256e61a4fbfe40db707cc1edeff32b5))
- Clarify that data migrations are lost ([`8826515`](https://github.com/browniebroke/django-remake-migrations/commit/88265151e84ea90e3297bf8f21a33b3a5f3acfa8))

## v2.7.0 (2025-03-29)

### Features

- Enable more complex migrations replacements ([`756bd1d`](https://github.com/browniebroke/django-remake-migrations/commit/756bd1d5b5bf496a897fc44c443d0511c55dc5dd))
- Allow all migrations replacing all migrations in an app ([`756bd1d`](https://github.com/browniebroke/django-remake-migrations/commit/756bd1d5b5bf496a897fc44c443d0511c55dc5dd))
- Allow replacing multiple apps ([`756bd1d`](https://github.com/browniebroke/django-remake-migrations/commit/756bd1d5b5bf496a897fc44c443d0511c55dc5dd))
- Add support for run_before ([`756bd1d`](https://github.com/browniebroke/django-remake-migrations/commit/756bd1d5b5bf496a897fc44c443d0511c55dc5dd))

### Documentation

- Tweaks docstrings to attempt improving the docs ([`756bd1d`](https://github.com/browniebroke/django-remake-migrations/commit/756bd1d5b5bf496a897fc44c443d0511c55dc5dd))
- More docs tweaks ([`756bd1d`](https://github.com/browniebroke/django-remake-migrations/commit/756bd1d5b5bf496a897fc44c443d0511c55dc5dd))
- Fix wrong claim about optimizations of operations ([`c0bce07`](https://github.com/browniebroke/django-remake-migrations/commit/c0bce075714c386788fd28f8c52339e046d4f99e))
- Add mikicz as a contributor for code, and ideas ([`4b15148`](https://github.com/browniebroke/django-remake-migrations/commit/4b15148320129734d4d40a7ebfa06f0dd023d544))

## v2.6.0 (2025-03-07)

### Features

- Add new command option to keep old migrations around ([`bc4b645`](https://github.com/browniebroke/django-remake-migrations/commit/bc4b645538d07334e7195cae4d6e4e7a0ef397cd))

## v2.5.0 (2025-02-18)

### Features

- Add django 5.2 support ([`2b9edce`](https://github.com/browniebroke/django-remake-migrations/commit/2b9edce796bd802c19389055796be3f86537d0cf))

### Testing

- Fix small flakyness due to __pycache__ folder ([`a647399`](https://github.com/browniebroke/django-remake-migrations/commit/a647399b5a721c5932fe5eb88d41340c8324cf14))

## v2.4.0 (2024-12-20)

### Features

- Migrate packaging to uv ([`c9eacf7`](https://github.com/browniebroke/django-remake-migrations/commit/c9eacf7ca91f17b6532056aecf036c7ca1010e75))

### Testing

- Fix flaky test due to time-dependency ([`4d1fc11`](https://github.com/browniebroke/django-remake-migrations/commit/4d1fc1103da936d2be06fd6780522ea35b880200))

## v2.3.0 (2024-11-26)

### Documentation

- Improve the documentation page for settings ([`fd8ae1a`](https://github.com/browniebroke/django-remake-migrations/commit/fd8ae1a4bbf0173ca0f8ec0adf6f7d7faa159cba))

### Features

- Add ability to specify database extensions ([`706fe3a`](https://github.com/browniebroke/django-remake-migrations/commit/706fe3aa72950de6f0ed975534b078ec1cef2010))

## v2.2.0 (2024-10-31)

### Features

- Drop support for python 3.8 ([`70302ee`](https://github.com/browniebroke/django-remake-migrations/commit/70302eeed10469a08011fbe279789d1da5c73fbd))

## v2.1.0 (2024-08-06)

### Features

- Add django 5.1 support ([`1782456`](https://github.com/browniebroke/django-remake-migrations/commit/1782456d0ca98c26acc3100b47c35b1910d6db04))

## v2.0.0 (2024-06-24)

### Features

- Drop django < 4.2 support ([`bc04435`](https://github.com/browniebroke/django-remake-migrations/commit/bc0443552f1115cc14efa8a7260d5ad753b2d426))

## v1.1.3 (2024-05-06)

### Bug fixes

- Update dependency django to v4.2.12 ([`d71d62d`](https://github.com/browniebroke/django-remake-migrations/commit/d71d62dc153b740ecfd5dc4d8f46915b1f2f6eed))

## v1.1.2 (2024-03-11)

### Bug fixes

- Update dependency django to v4.2.11 ([`c2abf8a`](https://github.com/browniebroke/django-remake-migrations/commit/c2abf8a78a319ca1d83b2e435c490eb764ca650d))

### Documentation

- Build docs on python 3.12 ([`394e5c1`](https://github.com/browniebroke/django-remake-migrations/commit/394e5c11da7848122649207e5fc6296423d983c8))

### Testing

- Reorganise test apps to enable adding more cases ([`c4fc2ee`](https://github.com/browniebroke/django-remake-migrations/commit/c4fc2ee86a7819fbb1ef92b6a6439f8a5658ce06))
- Refactor test case before adding more ([`c4fc2ee`](https://github.com/browniebroke/django-remake-migrations/commit/c4fc2ee86a7819fbb1ef92b6a6439f8a5658ce06))
- Refactor test fixture ([`c4fc2ee`](https://github.com/browniebroke/django-remake-migrations/commit/c4fc2ee86a7819fbb1ef92b6a6439f8a5658ce06))
- Extract context manager to setup apps for testing ([`c4fc2ee`](https://github.com/browniebroke/django-remake-migrations/commit/c4fc2ee86a7819fbb1ef92b6a6439f8a5658ce06))

## v1.1.1 (2024-02-06)

### Bug fixes

- Update dependency django to v4.2.10 ([`d0e7164`](https://github.com/browniebroke/django-remake-migrations/commit/d0e7164172be29abc9be0f2a90be5c6650601ea0))

## v1.1.0 (2024-01-24)

### Features

- Add settings to run some apps first and last ([`81e18c4`](https://github.com/browniebroke/django-remake-migrations/commit/81e18c42fc8432fbba2aeb07f5ef8052267aedef))
- Add setting to run other admin commands at the end ([`1f87053`](https://github.com/browniebroke/django-remake-migrations/commit/1f87053feafaaba326b132ae766d4f16f9317165))
- Improve logging of `remakemigrations` command ([`0688b8b`](https://github.com/browniebroke/django-remake-migrations/commit/0688b8b13a00288db493bd6ee173a7d207bce7bc))

### Bug fixes

- Simplify migration name generation ([`40a8b00`](https://github.com/browniebroke/django-remake-migrations/commit/40a8b00a5df1883cf328f2b7c3eaac454a55ad50))

## v1.0.0 (2023-11-15)

### Chores

- Rename package to django_remake_migrations ([`46612dd`](https://github.com/browniebroke/django-remake-migrations/commit/46612dd77ef96a0ebfe55d634171f25a7fd8a534))

## v0.3.2 (2023-11-01)

### Documentation

- Add dmytrolitvinov as a contributor for doc ([`03d4a0e`](https://github.com/browniebroke/django-remake-migrations/commit/03d4a0e286905ac8ff6be4dcab8363207a85032e))

### Bug fixes

- Typo in an url mentioned in the readme.md ([`58c3f5b`](https://github.com/browniebroke/django-remake-migrations/commit/58c3f5b8fbb5a8d3eb91768f7d97c4c8b06aa24e))

## v0.3.1 (2023-11-01)

### Bug fixes

- Update dependency django to v4.2.7 ([`c330296`](https://github.com/browniebroke/django-remake-migrations/commit/c3302963a8bdcd948fdbc53c24929b0719e16e26))

### Documentation

- Write the initial version of the docs ([`d3ac7c8`](https://github.com/browniebroke/django-remake-migrations/commit/d3ac7c82f66f7466f106e39ae0c6ac23b1f34a5a))

## v0.3.0 (2023-10-17)

### Testing

- Handle edge case on windows ([`7891b71`](https://github.com/browniebroke/django-remake-migrations/commit/7891b71426c33324ce8dc7ab0bf59bc5f88d64ba))
- Improve test cases by adding another app ([`2792b1c`](https://github.com/browniebroke/django-remake-migrations/commit/2792b1ca62d0fb077783a987f3e200ea9d38a769))

### Features

- Remove graph file and the need for base_dir setting ([`7ee4f06`](https://github.com/browniebroke/django-remake-migrations/commit/7ee4f0675ca851446ced74867f38fe943bcf94a4))
- Remake all migrations in one step ([`89c93e4`](https://github.com/browniebroke/django-remake-migrations/commit/89c93e4afe265bf3269dd634e258524184bae3ec))

### Bug fixes

- Invalidate imported migration modules when they are removed ([`7b5da27`](https://github.com/browniebroke/django-remake-migrations/commit/7b5da27bbd98cc640ae26e723eff7330573f763a))

## v0.2.1 (2023-10-17)

### Bug fixes

- Replaces property should be a list of tuples ([`0e88afe`](https://github.com/browniebroke/django-remake-migrations/commit/0e88afe164add8f4d888cabfd05b1e9d41b144d3))

## v0.2.0 (2023-10-13)

### Testing

- Fix flakyness with files order ([`4206edb`](https://github.com/browniebroke/django-remake-migrations/commit/4206edbda6ecb9803821ec4d4885d35c6b93a763))
- Set pythondontwritebytecode=1 ([`5a75506`](https://github.com/browniebroke/django-remake-migrations/commit/5a75506f6082b85a78d396585e490de0d0e499f3))
- Write test for step 2 and 3 ([`12d5a70`](https://github.com/browniebroke/django-remake-migrations/commit/12d5a70659e3f0a93c0b76dcdafb46425a529dcf))
- Generate coverage report as xml ([`ea8dfdc`](https://github.com/browniebroke/django-remake-migrations/commit/ea8dfdc1946e6e441b7e4a4eca269f9da07b2e82))
- Setup tox ([`9627c64`](https://github.com/browniebroke/django-remake-migrations/commit/9627c64ad2ab52dc649bfd986c7cdec6611de6e6))
- Add pytest-django ([`e21d3ef`](https://github.com/browniebroke/django-remake-migrations/commit/e21d3ef4d93e5e548340ae6194cdbe1fa63084d9))
- Scaffold a test app ([`cf5218f`](https://github.com/browniebroke/django-remake-migrations/commit/cf5218f73e2247912ccca34b2637adff91dcd59c))

### Features

- Declare official support for django 5.0 ([`aa1c465`](https://github.com/browniebroke/django-remake-migrations/commit/aa1c465329ab90bd19d0c5fa165f095b329c40f0))

### Bug fixes

- Change file type for graph file from pickle to json ([`5153293`](https://github.com/browniebroke/django-remake-migrations/commit/515329355cc614049ed5146a665a4bda3242b485))

## v0.1.0 (2023-10-09)

### Features

- First version of the command ([`00e761c`](https://github.com/browniebroke/django-remake-migrations/commit/00e761ccfbef62156b74c4445f1bc825bad71aca))

### Documentation

- Add @browniebroke as a contributor ([`33a03d3`](https://github.com/browniebroke/django-remake-migrations/commit/33a03d3f0859bf6b416523f63b54c3e279f52e95))
