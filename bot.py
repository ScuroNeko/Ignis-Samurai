from handler.handler import Handler
from settings import Settings
from utils.database import Database
from utils.logger import Logger


class Bot:
    def __init__(self, settings):
        self.settings = settings
        Logger()
        Database('name', 'user', 'password', 'localhost')

    def run(self):
        handler = Handler(self.settings)
        handler.init()
        handler.run()


if __name__ == '__main__':
    bot = Bot(Settings)
    bot.run()
