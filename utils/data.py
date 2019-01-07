import threading
from enum import Enum

import asyncio
import requests
from discord import HTTPException
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.longpoll import VkLongPoll

from utils import utils


event_ids = {4: 'message_new', 61: 'message_typing_state'}


class Event:
    __slots__ = ('api', 'type', 'meta')

    def __init__(self, api, event_type):
        self.api = api
        self.type = event_type
        self.meta = {}


class EventType(Enum):
    Longpoll = 0
    ChatChange = 1
    Callback = 2


class VkMessage:
    def __init__(self, session, message_data):
        self.message_data = message_data['object']
        self.session = session
        self.api = session.get_api()

        self.date = self.message_data['date']

        self.user_id = self.message_data['from_id']
        self.msg_id = self.message_data['id']
        self.peer_id = self.message_data['peer_id']

        self.is_chat = self.peer_id - 2000000000 > 0
        self.chat_id = self.peer_id - 2000000000

        self.original_text = self.message_data['text']
        self.full_text = self.message_data['text'].split(sep='] ')[::-1][0].lower() \
            if self.original_text.startswith('[club{}|'.format(utils.get_self_id(self.api))) \
            else self.message_data['text'].lower()
        self.text = self.message_data['text'].split(sep='] ')[::-1][0].lower() \
            if self.full_text.startswith('[club{}|'.format(utils.get_self_id(self.api))) \
            else self.message_data['text'].lower()

        self.forwarded_messages = self.message_data['fwd_messages']
        self.attachments = self.message_data['attachments']

        self.meta = {}

    def answer(self, msg, attachments='', keyboard=None):
        data = {'peer_id': self.peer_id,
                'message': msg}
        if attachments:
            if isinstance(attachments, str):
                attachments = attachments
            elif isinstance(attachments, (set, frozenset, tuple, list)):
                attachments = ','.join(attachments)
            data.update({'attachment': attachments})

        if keyboard:
            data.update({'keyboard': keyboard.get_keyboard()})

        return self.api.messages.send(**data)


class VkEvent:
    def __init__(self, session, raw_event):
        self.raw = raw_event['object']
        self.session = session

        self.date = self.raw['date']
        self.user_id = self.raw['from_id']
        self.peer_id = self.raw['peer_id']

        self.action = self.raw['action']
        self.type = self.action['type']

        self.member_id = self.action['member_id'] if self.type in ['chat_kick_user', 'chat_invite_user',
                                                                   'chat_unpin_message', 'chat_pin_message'] else 0

        self.message_id = self.action['conversation_message_id'] if self.type in ['chat_unpin_message', 'chat_pin_message'] else 0
        self.text = self.action['text'] if self.type in ['chat_title_update'] else ''


class VkLongpollEvent(Event):
    def __init__(self, api, raw_data):
        super().__init__(api, EventType.Longpoll)
        self.data = raw_data
        self.type = raw_data['type']
        self.user_id = raw_data['object']['from_id']
        self.peer_id = raw_data['object']['peer_id'] if 'peer_id' in raw_data['object'] else self.user_id
        self.action = 'message_new' if 'action' not in raw_data['object'] else raw_data['object']['action']['type']

    def __str__(self):
        return f'LongpollEvent ({self.type})'


class DSMessage:
    def __init__(self, message, client):
        self.message = message
        self.client = client

        self.edited_timestamp = message.edited_timestamp
        self.timestamp = message.timestamp
        self.tts = message.tts
        self.text = message.content
        self.channel = message.channel
        self.mention_everyone = message.mention_everyone
        self.embeds = message.embeds
        self.id = message.id
        self.mentions = message.mentions
        self.author = message.author
        self.channel_mentions = message.channel_mentions
        self.server = message.server
        self.attachments = message.attachments
        self.nonce = message.nonce
        self.pinned = message.pinned
        self.role_mentions = message.role_mentions
        self.type = message.type
        self.call = message.call
        self.reactions = message.reactions

        self.meta = {}

    def answer(self, text='', embed=None, tts=False):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.client.send_message(self.channel, text, embed=embed, tts=tts))
            loop.close()
        except (HTTPException, RuntimeError):
            pass


class MyVkBotLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except requests.ReadTimeout:
                self.session = requests.Session()
                self.update_longpoll_server()


class MyVkLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except requests.ReadTimeout:
                self.session = requests.Session()
                self.update_longpoll_server()


class StoppableThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         args=args, kwargs=kwargs, daemon=daemon)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
