Current state: **alpha**, yet API seems fine and mostly stable.

In current version (0.5.x) new-high level API is introduced while older low-level API partially marked as deprecated.

* Works on Python 3.4+
* Has support for PostgreSQL via `aiopg`
* Has support for MySQL via `aiomysql`
* Single point for high-level async API
* Drop-in replacement for sync code, sync will remain sync
* Basic operations are supported
* Transactions support is present, yet not heavily tested

The source code is hosted on `GitHub`_.

.. _GitHub: https://github.com/05bit/peewee-async


