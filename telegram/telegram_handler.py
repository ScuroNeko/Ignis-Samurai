import traceback

from py_telegram_bot.bot import Bot

from base.base_handler import BaseHandler
from base.base_plugin import BasePlugin
from telegram.telegram_plugin import TelegramBasePlugin
from vk.vk_handler import VKHandler


class TelegramMessage:
    def __init__(self, raw, bot):
        self.raw = raw
        self.api = bot.get_api()
        self.uploader = bot.get_uploader()
        self.message_id = raw.message_id

        # USER INFO
        self.user_id = raw['from']['id']
        self.from_bot = raw['from']['is_bot']
        self.from_first_name = raw['from']['first_name']
        self.from_username = raw['from']['username']
        self.from_lang_code = raw['from'].get('language_code', '')

        # CHAT INFO
        self.chat_id = raw.chat.id
        self.chat_type = raw.chat.type

        self.date = raw.date
        self.text = raw.get('text', '')

        self.meta = {}

    def answer(self, text, attachment: dict = None, keyboard=None):
        if not text and not attachment:
            return
        data = {'chat_id': self.chat_id}
        if not attachment:
            if keyboard:
                data.update({'text': text, 'reply_markup': keyboard})
            else:
                data.update({'text': text})
            self.api.send_message(**data)
        else:
            data.update({'caption': text, 'photo': attachment['file']})
            if attachment['type'] == 'photo':
                self.uploader.send_photo(**data)


class TelegramHandler(BaseHandler):
    bot = None
    plugins = None

    def __init__(self, settings, logger):
        super().__init__()

        self.thread = None
        token = ''
        for auth in settings.auth:
            if auth[0] == 'telegram':
                token = auth[1]

        self.bot = Bot(token, proxy_type='socks5', proxy_url='proxy:Nix13789@nix13.xyz:8080')
        self.logger = logger

        self.plugins = []
        for p in settings.plugins:
            if isinstance(p, TelegramBasePlugin):
                p.set_up(self.bot)
                self.plugins.append(p)
            if isinstance(p, BasePlugin):
                p.set_up(self.bot, VKHandler.session)
                self.plugins.append(p)
        TelegramHandler.plugins = self.plugins

    def run(self):
        self.thread.start()

    def listen(self, settings):
        for update in self.bot.get_updates():
            try:
                self.check(TelegramMessage(update, self.bot))
            except:
                self.logger.error(traceback.format_exc())

    def init(self):
        for p in self.plugins:
            p.init()

    def check(self, msg):
        for p in self.plugins:
            if p.check_msg(msg):
                p.process_msg(msg)
                break
