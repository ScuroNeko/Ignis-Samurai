from peewee import PostgresqlDatabase, MySQLDatabase

from utils.logger import Logger


class Database:
    db = None

    def __init__(self, settings):
        db_settings: dict = settings.database

        driver_name = db_settings.get('driver', '')
        host = db_settings.get('host', 'localhost')
        name = db_settings.get('name', '')
        user = db_settings.get('user', 'root')
        password = db_settings.get('password', '')
        port = db_settings.get('port')

        if driver_name.lower() in ('postgres', 'postgresql', 'psql'):
            driver = PostgresqlDatabase
            if not port:
                port = 5432
        elif driver_name.lower() == 'mysql':
            driver = MySQLDatabase
            if not port:
                port = 3306
        else:
            return

        Database.db = driver(name, user=user, password=password, host=host, port=port)
        Database.db.connect()
        Logger.log.info('Connected to database')

        from utils.database.models import Models
        Models.init()
