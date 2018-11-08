from enum import Enum


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
    def __init__(self, message_data, api):
        self.message_data = message_data
        self.api = api

        self.date = self.message_data['date']
        self.user_id = self.message_data['from_id']
        self.msg_id = self.message_data['id']
        self.peer_id = self.message_data['peer_id']
        self.text = self.message_data['text']
        self.forwarded_messages = self.message_data['fwd_messages']
        self.attachments = self.message_data['attachments']

        self.meta = {}

    async def answer(self, msg, attachments=None):
        if attachments:
            pass
        self.api.messages.send(peer_id=self.peer_id,
                               message=msg)


class LongpollEvent(Event):
    __slots__ = ('event_data', 'id')

    def __init__(self, api, event_id, event_data):
        super().__init__(api, EventType.Longpoll)

        self.id = event_id
        self.event_data = event_data

    def __str__(self):
        return f"LongpollEvent ({self.id}, {self.event_data[1] if len(self.event_data) > 1 else '_'})"
