import peewee
from handler.base_plugin import BasePlugin


class PeeweePlugin(BasePlugin):
    __slots__ = ('database', 'manager', 'set_manager')

    def __init__(self, host, name, user, password, port=None, custom_driver=None, set_manager=True, **kwargs):
        """Adds self to messages and event's `data` field.
        Through this instance you can access peewee_async.Manager instance (data["peewee_async"].manager).
        This plugin should be included first!
        """

        super().__init__()

        self.set_manager = set_manager

        if custom_driver is None or custom_driver == 'PostgreSQL':
            driver = peewee.PostgresqlDatabase
            if port is None:
                port = 5432
        elif custom_driver == 'MySQL':
            driver = peewee.MySQLDatabase
            if port is None:
                port = 3306
        else:
            driver = custom_driver

        if isinstance(port, str):
            try:
                port = int(port)
            except ValueError:
                raise ValueError('Port is wrong!')

        self.database = driver(name, user=user, password=password, host=host, port=port, **kwargs)

    def init(self):
        if self.set_manager:
            for plugin in self.handler.plugins:
                if hasattr(plugin, 'db'):
                    plugin.db = self.database

    def before_check(self, msg):
        msg.meta['db'] = self
