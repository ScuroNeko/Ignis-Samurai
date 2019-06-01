import traceback

import requests
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from base.base_handler import BaseHandler
from base.base_plugin import BasePlugin
from vk.vk_plugin import VKBasePlugin


class VKMessage:
    def __init__(self, session, raw):
        self.raw = raw['object']
        self.session = session
        self.api = session.get_api()

        self.original_text = self.raw['text']
        self.text = ' '.join(self.original_text.lower().split()[1:]) \
            if self.original_text.lower().startswith('[club171962231|') \
            else self.original_text.lower()
        self.user_id = self.raw['from_id']
        self.peer_id = self.raw['peer_id']
        self.date = self.raw['date']

        self.from_first_name = self.api.users.get(user_ids=self.user_id)[0]['first_name']

        self.meta = {}

    def answer(self, text, attachments=None, keyboard=None):
        data = {'peer_id': self.peer_id}
        if text:
            data.update({'message': text})
        if keyboard:
            data.update({'keyboard': keyboard})
        if attachments:
            if isinstance(attachments, (set, tuple, list, frozenset)):
                attachments = ','.join(attachments)
            data.update({'attachment': attachments})
        if attachments is not None or text is not None:
            self.api.messages.send(**data)


class VKHandler(BaseHandler):
    session = None
    plugins = []

    def __init__(self, settings, logger):
        super().__init__()

        self.session = VkApi(token=settings.auth[0][1], api_version='5.89')
        VKHandler.session = self.session
        self.plugins = []
        for p in settings.plugins:
            from telegram.telegram_handler import TelegramHandler
            if isinstance(p, VKBasePlugin):
                p.set_up(self.session)
                self.plugins.append(p)
            if isinstance(p, BasePlugin):
                p.set_up(TelegramHandler.bot, self.session)
                self.plugins.append(p)
        VKHandler.plugins = self.plugins

        self.logger = logger
        self.thread = None

    def run(self):
        self.thread.start()

    def listen(self, settings):
        longpoll = LongPoll(self.session, settings.auth[0][2])
        while True:
            try:
                for event in longpoll.check():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        try:
                            self.check(VKMessage(self.session, event.raw))
                        except:
                            self.logger.error(traceback.format_exc())
            except KeyboardInterrupt:
                break

    def init(self):
        for p in self.plugins:
            p.init()

    def check(self, msg):
        for p in self.plugins:
            if p.check_msg(msg):
                p.process_msg(msg)
                break


class LongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except requests.ReadTimeout:
                self.session = requests.Session()
                self.update_longpoll_server()
