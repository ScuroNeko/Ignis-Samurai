import asyncio
import traceback

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType

from handler.message import Message
from settings import Settings
from utils.logger import Logger
from utils.vk_utils import get_self_id


class Handler:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = None
        self.api = None

        self.plugins = []

    def init(self):
        if not self.settings.token:
            Logger.log.error('No access token!')
            exit()
        self.session = VkApi(token=self.settings.token)
        self.api = self.session.get_api()
        group = self.api.groups.getById()[0]
        Logger.log.info(f'Login as {group["name"]} (https://vk.com/public{group["id"]})')

        for p in self.settings.plugins:
            for init in p.init_methods:
                Logger.log.debug(f'Init: {p.__class__.__name__}')
                init.init()
            self.plugins.append(p)

    async def check(self, msg: Message):
        text = msg.text
        payload = msg.payload['cmd'] if 'cmd' in msg.payload else ''

        for p in self.plugins:
            if payload in p.payloads.keys():
                try:
                    await p.payloads[payload](msg)
                except:
                    Logger.log.error(traceback.format_exc())
                break

        for prefix in self.settings.prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        else:
            return

        for p in self.plugins:
            if text in p.commands.keys():
                try:
                    await p.commands[text](msg)
                except:
                    Logger.log.error(traceback.format_exc())
                break

    def run(self):
        lp = VkBotLongPoll(self.session, get_self_id(self.api))
        for event in lp.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = Message(self.session, self.api, event.obj)
                asyncio.new_event_loop().run_until_complete(self.check(msg))
