from handler.handler import Handler
from utils.database.database import Database
from utils.logger import Logger


class Bot:
    __slots__ = ('settings', 'is_running', 'middlewares')

    def __init__(self, settings):
        Logger()
        Database(settings)
        self.settings = settings
        self.is_running = False
        self.middlewares = []

    def add_plugin(self, plugin):
        if self.is_running:
            Logger.log.error('Bot already running!')
        self.settings.plugins.append(plugin)

    def add_prefix(self, prefix):
        if self.is_running:
            Logger.log.error('Bot already running!')
        self.settings.prefixes.append(prefix)

    def add_middleware(self, middleware):
        if self.is_running:
            Logger.log.error('Bot already running!')
        self.middlewares.append(middleware)

    def run(self):
        handler = Handler(self.settings, self.middlewares)
        handler.init()
        try:
            self.is_running = True
            handler.run()
        except KeyboardInterrupt:
            handler.shutdown()
            if Database.db and not Database.db.is_closed():
                Database.db.close()
