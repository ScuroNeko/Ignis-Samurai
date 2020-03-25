from peewee import OperationalError
from handler.handler import Handler
from settings import Settings
from utils.database.database import Database
from utils.logger import Logger


class Bot:
    __slots__ = ('settings',)

    def __init__(self, settings):
        Logger()
        Database(settings)
        self.settings = settings

    def run(self):
        handler = Handler(self.settings)
        handler.init()
        try:
            handler.run()
        except OperationalError:
            if Database.db and Database.db.is_closed():
                Database.db.connect()
        except KeyboardInterrupt:
            handler.shutdown()
            if Database.db and not Database.db.is_closed():
                Database.db.close()

