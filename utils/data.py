from enum import Enum

from utils import utils


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


class Message:
    def __init__(self, api, message_data):
        self.message_data = message_data
        self.api = api

        self.date = self.message_data['date']

        self.user_id = self.message_data['from_id']
        self.msg_id = self.message_data['id']
        self.peer_id = self.message_data['peer_id']

        self.full_text = self.message_data['text']
        self.text = self.message_data['text'].split(sep='] ')[::-1][0].lower() \
            if self.full_text.startswith('[club{}|'.format(utils.get_self_id(self.api))) \
            else self.message_data['text']

        self.forwarded_messages = self.message_data['fwd_messages']
        self.attachments = self.message_data['attachments']

        self.meta = {}

    async def answer(self, msg, attachments=''):
        if attachments:
            if isinstance(attachments, str):
                attachments = attachments
            elif isinstance(attachments, (set, frozenset, tuple, list)):
                attachments = ','.join(attachments)
        self.api.messages.send(peer_id=self.peer_id,
                               message=msg,
                               attachment=attachments)
        return


class LongpollEvent(Event):
    def __init__(self, api, raw_data):
        super().__init__(api, EventType.Longpoll)
        self.data = raw_data
        self.type = raw_data['type']
        self.user_id = raw_data['object']['from_id']
        self.peer_id = raw_data['object']['peer_id'] if 'peer_id' in raw_data['object'] else self.user_id
        self.action = 'message_new' if 'action' not in raw_data['object'] else raw_data['object']['action']['type']

    def __str__(self):
        return f'LongpollEvent ({self.type})'
