import asyncio
import logging
import random
import traceback

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from base.base_handler import BaseHandler
from vk.vk_plugin import VKBasePlugin


class VKMessage:
    def __init__(self, raw, session):
        self.raw = raw
        self.session = session
        self.api = session.get_api()

        self.date = self.raw.get('date', 0)

        self.user_id = self.raw['from_id']
        self.peer_id = self.raw.get('peer_id', 0)
        self.is_chat = self.peer_id - 2000000000 > 0
        self.chat_id = self.peer_id - 2000000000 if self.peer_id - 2000000000 > 0 else 0

        self.original_text = self.raw['text'].split('] ')[1] if self.raw['text'].startswith('[club') else self.raw['text']
        self.text = self.original_text.lower()
        self.full_text = self.raw['text']

        self.msg_id = self.raw['conversation_message_id']
        self.forwarded_msgs = self.raw['fwd_messages']
        self.attachments = self.raw['attachments']

        self.meta = dict()

    def answer(self, text='', attachments=None):
        if not text and attachments is None:
            return
        data = {'peer_id': self.peer_id,
                'random_id': random.randint(-99**99, 99**99)}
        if text:
            data.update({'message': text})
        if attachments:
            data.update({'attachment': ','.join(attachments)})
        return self.api.messages.send(**data)


class VKHandler(BaseHandler):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.plugins = []
        self.session = VkApi(token=settings.auth[0][1])
        self.api = self.session.get_api()
        self.loop = asyncio.new_event_loop()

        for p in self.settings.plugins:
            if isinstance(p, VKBasePlugin):
                p.set_up(self.api, self.session, self)
                self.plugins.append(p)

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
        for p in self.plugins:
            await p.pre_check_msg(msg)
            if await p.check_msg(msg):
                await p.post_check_msg(msg)
                await p.pre_process_msg(msg)
                await p.process_msg(msg)
                await p.post_process_msg(msg)
                return 

    def listen(self):
        lp = VkBotLongPoll(self.session, self.api.groups.getById()[0]['id'])
        for event in lp.listen():
            try:
                if event.type == VkBotEventType.MESSAGE_NEW:
                    self.loop.run_until_complete(self.check(VKMessage(event.object, self.session)))
            except KeyboardInterrupt:
                self.loop.close()
                break
            except:
                logging.error(traceback.format_exc())
