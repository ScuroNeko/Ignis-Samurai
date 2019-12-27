import asyncio
import traceback

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType

from handler.event import ChatEvent, Event
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
                init.call()
            self.plugins.append(p)

    async def check(self, msg: Message):
        text = msg.text
        payload = msg.payload['cmd'] if 'cmd' in msg.payload else ''
        args = msg.payload['args'] if 'args' in msg.payload else []

        for p in self.plugins:
            if p.custom_checker:
                try:
                    for before_process in p.before_process_methods:
                        before_process()
                    return await p.custom_checker(msg, p)
                except Exception:
                    Logger.log.info(traceback.format_exc())

            
            if payload in p.payloads.keys():
                try:
                    msg.meta.update({'args': args})

                    for before_process in p.before_process_methods:
                        before_process.call()
                    return await p.payloads[payload](msg)
                except:
                    Logger.log.error(traceback.format_exc())

        for prefix in self.settings.prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        else:
            return

        for p in self.plugins:
            for command in p.commands.keys():
                if text.startswith(command):
                    try:
                        args = text[len(command)+1:].split()
                        msg.meta.update({'args': args})

                        for before_process in p.before_process_methods:
                            before_process.call()
                        return await p.commands[text[:len(command)]](msg)
                    except:
                        Logger.log.error(traceback.format_exc())


    async def check_event(self, event: (ChatEvent, Event), msg: (Message, None)):
        event_type = event.type

        for plugin in self.plugins:
            if event_type in plugin.chat_events.keys():
                try:
                    for before_process in plugin.before_process_methods:
                        before_process.call()
                    return await plugin.chat_events[event_type](event, msg)
                except:
                    Logger.log.error(traceback.format_exc())
            
            elif event_type in plugin.events.keys():
                try:
                    for before_process in plugin.before_process_methods:
                        before_process.call()
                    return await plugin.events[event_type](event)
                except:
                    Logger.log.error(traceback.format_exc())

    def run(self):
        lp = VkBotLongPoll(self.session, get_self_id(self.api))
        for event in lp.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and 'action' not in event.obj:
                msg = Message(self.session, self.api, event.obj)
                asyncio.new_event_loop().run_until_complete(self.check(msg))

            elif event.type == VkBotEventType.MESSAGE_NEW and 'action' in event.obj:
                evnt = ChatEvent(self.session, self.api, event.obj['action'])
                msg = Message(self.session, self.api, event.obj)
                asyncio.new_event_loop().run_until_complete(self.check_event(evnt, msg))
                
            else:
                evnt = Event(self.session, self.api, event.raw)
                asyncio.new_event_loop().run_until_complete(self.check_event(evnt, None))
