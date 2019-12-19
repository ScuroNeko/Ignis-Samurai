from peewee_async import PostgresqlDatabase, MySQLDatabase, Manager


class Database:
    db = None

    def __init__(self, name, user, password, host, port=5432, driver_name='postgres', **kwargs):
        if driver_name.lower() in ('postgres', 'postgresql', 'psql'):
            driver = PostgresqlDatabase
        elif driver_name.lower() == 'mysql':
            driver = MySQLDatabase
        else:
            return

        database = driver(name, user=user, password=password, host=host, port=port, **kwargs)
        Database.db = Manager(database)
        database.set_allow_sync(False)
