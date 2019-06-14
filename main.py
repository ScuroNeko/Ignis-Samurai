import logging
import traceback
from threading import Thread

from plugins.about import About
from plugins.balance import BalancePlugin
from plugins.echo import Echo
from telegram.tg_handler import TelegramHandler
from utils.peewee import PeeweePlugin
from vk.vk_handler import VKHandler


class Bot:
    def __init__(self, settings):
        self.settings = settings
        level = logging.DEBUG if settings.debug else logging.INFO
        logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(filename)s: %(message)s',
                            level=level, datefmt='%H:%M:%S %d.%m.%Y', handlers=[logging.StreamHandler(),
                                                                                logging.FileHandler('log.txt')])
        self.running = False

    def run(self):
        if self.running:
            logging.error('Bot already running')
        for h in self.settings.handlers:
            handler = h(self.settings)
            try:
                handler.init()
            except:
                logging.error(traceback.format_exc())
            Thread(target=handler.listen).start()
            logging.info(f'Started {handler.name}')

    def add_auth(self, name, *data):
        if self.running:
            logging.error('Bot already running')
        self.settings.auth.append([name, *data])

    def add_handler(self, handler):
        if self.running:
            logging.info('Bot already running')
        self.settings.handlers.append(handler)

    def add_plugin(self, plugin):
        if self.running:
            logging.error('Bot already running')
        self.settings.plugins.append(plugin)

    def add_prefix(self, prefix: str):
        if self.running:
            logging.error('Bot already running')
        self.settings.prefixes.append(prefix)


class Settings:
    handlers = []
    prefixes = []
    auth = []
    debug = False

    plugins = [
        PeeweePlugin('name', 'user',
                     'password',
                     'host'),
        Echo(prefixes),
        BalancePlugin(prefixes),
    ]


if __name__ == '__main__':
    bot = Bot(Settings)
    bot.add_handler(VKHandler)
    bot.add_handler(TelegramHandler)
    bot.add_auth('vk', 'token')
    bot.add_auth('telegram', 'token')

    bot.add_prefix('!')

    bot.add_plugin(About(Settings.prefixes))

    bot.run()
