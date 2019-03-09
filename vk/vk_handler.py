import traceback

import requests
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from base.base_handler import BaseHandler


class VKMessage:
    def __init__(self, session, raw):
        self.raw = raw['object']
        self.session = session
        self.api = session.get_api()

        self.text = self.raw['text']
        self.user_id = self.raw['from_id']
        self.peer_id = self.raw['peer_id']
        self.date = self.raw['date']

    def answer(self, text, attachments=None):
        data = {'peer_id': self.peer_id}
        if text is not None:
            data.update({'message': text})
        if attachments is not None:
            if isinstance(attachments, (set, tuple, list, frozenset)):
                attachments = ','.join(attachments)
            data.update({'attachment': attachments})
        if attachments is not None or text is not None:
            self.api.messages.send(**data)


class VKHandler(BaseHandler):
    def __init__(self, settings, logger):
        super().__init__()

        self.session = VkApi(token=settings.auth[0][1], api_version='5.89')
        self.plugins = []
        for plugin in settings.plugins:
            if isinstance(plugin, VKBasePlugin):
                self.plugins.append(plugin)
        self.logger = logger
        self.running = True
        self.thread = None

    def run(self):
        self.thread.start()

    def listen(self, settings):
        longpoll = LongPoll(self.session, settings.auth[0][2])
        try:
            while self.running:
                for event in longpoll.check():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        try:
                            self.check(VKMessage(self.session, event.raw))
                        except:
                            self.logger.error(traceback.format_exc())
                if not self.running:
                    break
        except KeyboardInterrupt:
            self.running = False
            self.thread.stop()

    def init(self):
        for p in self.plugins:
            p.init()

    def check(self, msg):
        for p in self.plugins:
            if p.check_msg(msg):
                p.process_msg(msg)


class VKBasePlugin:
    __slots__ = ('name', 'api', 'session')

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.api = None
        self.session = None

    def set_up(self, api, session):
        self.api = api
        self.session = session

    def init(self):
        ...

    def check_msg(self, msg) -> bool:
        ...

    def process_msg(self, msg) -> None:
        ...


class VKCommandPlugin(VKBasePlugin):
    def __init__(self, prefixes, commands):
        super().__init__()
        self.prefixes = prefixes
        self.commands = commands

    def check_msg(self, msg):
        text = ''
        for p in self.prefixes:
            if msg.text.startswith(p):
                text = msg.text[len(p):]
                if text.startswith(' '):
                    text = msg.text[1:]

        for c in self.commands:
            if text.startswith(c):
                return True
            break

        return False


class LongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except requests.ReadTimeout:
                self.session = requests.Session()
                self.update_longpoll_server()
