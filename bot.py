import logging
from threading import Thread

from plugins.test_vk import TestVK
from vk.vk_handler import VKHandler


class Bot:
    def __init__(self, settings):
        self.settings = settings

        self.logger = None
        self.logger_file = None
        self.__init_logger()

        self.is_running = False

    def run(self):
        if self.is_running:
            self.logger.error('Bot already running!')
            return
        for handler in self.settings.handlers:
            handler = handler(self.settings, self.logger)
            handler.init()
            handler.thread = Thread(target=handler.listen, args=(self.settings,), name=handler.name)
            handler.run()
            self.logger.info('{} successful started!'.format(handler.name))
        self.is_running = True

    def add_plugin(self, plugin):
        if self.is_running:
            self.logger.error('Bot already running! You can\'t add plugin after starting bot!')
        else:
            for p in self.settings.plugins:
                if p.name == plugin.name:
                    self.logger.error('Plugin with name "{}" already added!'.format(plugin.name))
                    break
            self.settings.plugins.append(plugin)
            self.logger.debug('"{}" successful added!'.format(plugin.name))

    def add_prefix(self, prefix):
        if self.is_running:
            self.logger.error('Bot already running! You can\'t add prefix after starting bot!')
        elif prefix in self.settings.prefixes:
            self.logger.error('Prefix "{}" already added!'.format(prefix))
        else:
            self.settings.prefixes.append(prefix)
            self.logger.debug('"{}" successful added!'.format(prefix))

    def add_handler(self, handler):
        if self.is_running:
            self.logger.error('Bot already running! You can\'t add handler after starting bot!')
        else:
            self.settings.handlers.append(handler)
            self.logger.debug('"{}" successful added!'.format(handler.name))

    def __init_logger(self):
        formatter = logging.Formatter(fmt='%(filename)s [%(asctime)s] %(levelname)s: %(message)s',
                                      datefmt='%d.%m.%Y %H:%M:%S')
        level = logging.DEBUG if self.settings.debug else logging.INFO
        self.logger = logging.Logger('bot', level=level)

        file_handler = logging.FileHandler('log.txt')
        file_handler.setLevel(level=level)
        file_handler.setFormatter(formatter)
        self.logger_file = file_handler

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=level)
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)


class Settings:
    # VK group auth
    auth = (('vk', '', 000000),
            ('telegram', ''))

    debug = False

    handlers = []
    prefixes = ['бот ', 'бот, ', '/']
    plugins = []


if __name__ == '__main__':
    bot = Bot(Settings)
    bot.add_handler(VKHandler)
    bot.add_plugin(TestVK(Settings.prefixes))
    bot.add_prefix('!')
    bot.run()
