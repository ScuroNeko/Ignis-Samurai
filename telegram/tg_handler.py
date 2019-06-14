import asyncio
import logging

from py_telegram_bot.bot import Bot

from base.base_handler import BaseHandler
from telegram.tg_plugin import TelegramBasePlugin


class TelegramHandler(BaseHandler):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.plugins = []
        self.bot = Bot(token=settings.auth[1][1], proxy_type='socks5', proxy_url='proxy:Nix13789@nix13.xyz:5080')
        self.loop = asyncio.new_event_loop()
        for p in self.settings.plugins:
            if isinstance(p, TelegramBasePlugin):
                self.plugins.append(p)
                p.set_up(self.bot)

    def init(self):
        for p in self.plugins:
            logging.debug(f'Pre-Init: {p.name}')
            p.pre_init()

        for p in self.plugins:
            logging.debug(f'Init: {p.name}')
            p.init()

        for p in self.plugins:
            logging.debug(f'Post-Init: {p.name}')
            p.post_init()

    async def check(self, msg):
        for plugin in self.plugins:
            await plugin.pre_check_msg(msg)
            if await plugin.check_msg(msg):
                await plugin.post_check_msg(msg)
                await plugin.pre_process_msg(msg)
                await plugin.process_msg(msg)
                await plugin.post_process_msg(msg)
                return

    def listen(self):
        for update in self.bot.get_updates():
            self.loop.run_until_complete(self.check(update))


