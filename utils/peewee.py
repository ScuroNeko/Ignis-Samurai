import logging

from peewee_async import PostgresqlDatabase, MySQLDatabase, Manager

from vk.vk_plugin import VKBasePlugin


class PeeweePlugin(VKBasePlugin):
    __slots__ = ('database', 'manager', 'set_manager')

    def __init__(self, name, user, password, host, port=5432, driver_name='postgres', set_manager=True, **kwargs):
        super().__init__()

        self.set_manager = set_manager

        if driver_name == 'postgres':
            driver = PostgresqlDatabase
        elif driver_name == 'mysql':
            driver = MySQLDatabase
        else:
            logging.error('Wrong driver name')
            return

        self.database = driver(name, user=user, password=password, host=host, port=port, **kwargs)
        self.manager = Manager(self.database)
        self.database.set_allow_sync(False)

    def init(self):
        if self.set_manager:
            for plugin in self.handler.plugins:
                if hasattr(plugin, 'db'):
                    plugin.db = self.manager
