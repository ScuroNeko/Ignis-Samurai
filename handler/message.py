import json
from enum import Enum
from typing import Union, List, Type

from utils.vk.keyboard import VkKeyboard
from utils.vk_utils import generate_random_id


class MessageArgs(dict):
    def __init__(self, args: dict):
        self.__args: dict = args
        super().__init__(args)

    def __getattr__(self, item):
        try:
            return self.__args[item]
        except KeyError:
            return None


class VkObject:
    __slots__ = (
        'raw',
    )

    def __init__(self, raw):
        self.raw = raw


class PhotoSize:
    __slots__ = (
        'type', 'url', 'width', 'height'
    )

    def __init__(self, raw: dict):
        self.type: str = raw['type']
        self.url: str = raw['url']
        self.width: int = raw['width']
        self.height: int = raw['height']


class Photo(VkObject):
    __slots__ = (
        'id', 'album_id', 'owner_id',
        'user_id', 'text', 'date', 'sizes'
    )

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.raw: dict = raw['photo']
        self.id: int = self.raw['id']
        self.album_id: int = self.raw['album_id']
        self.owner_id: int = self.raw['owner_id']
        self.user_id: int = self.raw.get('user_id', 0)

        self.text: str = self.raw['text']
        self.date: int = self.raw['date']  # unix time
        self.sizes = [PhotoSize(r) for r in self.raw['sizes']]

    def __repr__(self):
        return f'photo{self.owner_id}_{self.id}'


class DocumentType(Enum):
    TEXT = 1
    ARCHIVE = 2
    GIF = 3
    PHOTO = 4
    AUDIO = 5
    VIDEO = 6
    BOOKS = 7
    UNKNOWN = 8


class Document(VkObject):
    __slots__ = (
        'id', 'album_id', 'owner_id',
        'title', 'size', 'ext', 'url',
        'date', 'type'
    )

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.raw: dict = raw['doc']
        self.id: int = self.raw['id']
        self.owner_id: int = self.raw['owner_id']

        self.title: str = self.raw['title']
        self.size: int = self.raw['size']  # размер в байтах
        self.ext: str = self.raw['ext']  # расширение
        self.url: str = self.raw['url']
        self.date: int = self.raw['date']  # unix time
        self.type: DocumentType = self.raw['type']

    def __repr__(self):
        return f'doc{self.owner_id}_{self.id}'


Attachment = Type[Photo], Type[Document]


def load_attachments(raw: List[dict]) -> Union[Attachment]:
    attachments = []
    for attachment in raw:
        if attachment['type'] == 'photo':
            attachments.append(Photo(attachment))
        elif attachment['type'] == 'doc':
            attachments.append(Document(attachment))
        else:
            attachments.append(VkObject(attachment))
    return attachments


def dump_attachments(raw_attachments: Union[Attachment]) -> str:
    mapped = map(str, raw_attachments)
    return ','.join(mapped)


class EventActions:
    SHOWSNACKBAR = 'show_snackbar'
    OPENLINK = 'open_link'
    OPENAPP = 'open_app'


class Message(VkObject):
    __slots__ = (
        'session', 'api', 'raw', 'id', 'conversation_message_id',
        'date', 'peer_id', 'from_id', 'user_id', 'chat_id', 'is_chat',
        'original_text', 'text', 'attachments', 'payload',
        'event_id', 'forwarded_messages', 'reply_message',
        'meta'
    )

    def __init__(self, session, api, raw):
        super().__init__(raw)

        self.session = session
        self.api = api
        if type(raw) == Message:
            self.raw = raw.raw
        else:
            self.raw = raw.get('message', raw)

        self.id: int = self.raw.get('id', 0)
        self.conversation_message_id: int = self.raw.get('conversation_message_id', 0)
        self.date: int = self.raw.get('date', 0)

        self.peer_id: int = self.raw['peer_id']
        self.from_id: int = self.raw.get('from_id', 0)
        self.user_id: int = self.raw.get('user_id', self.raw.get('from_id', 0))

        self.chat_id: int = self.peer_id - 2000000000
        self.is_chat: bool = self.chat_id > 0

        self.original_text: str = self.raw.get('text', '')
        self.text: str = self.original_text.lower()

        self.attachments: Union[Attachment] = load_attachments(self.raw.get('attachments', []))

        raw_payload = self.raw.get('payload', '{}')
        if type(raw_payload) == dict:
            self.payload: dict = raw_payload
        else:
            self.payload: dict = json.loads(raw_payload)

        self.event_id: str = self.raw.get('event_id', '')

        self.forwarded_messages: list = self.raw.get('fwd_messages', [])
        self.reply_message = Message(self.session, self.api, self.raw['reply_message']) \
            if 'reply_message' in self.raw else None

        self.meta: dict = {}

    async def send(self, peer_id, text: str = '', attachments: (Union[Attachment], Attachment) = '', **kwargs):
        data = kwargs.copy()
        data.update({
            'peer_id': peer_id,
            'random_id': generate_random_id()
        })

        if text:
            data.update({'message': text})

        if attachments:
            if type(attachments) == str:
                data.update({'attachment': attachments})
            elif type(attachments) in (Photo, Document):
                data.update({'attachment': str(attachments)})
            else:
                data.update({'attachment': dump_attachments(attachments)})

        await self.api.messages.send(**data)

    async def answer_event(self, event_data):
        data = {
            'peer_id': self.peer_id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'event_data': json.dumps(event_data),
        }

        await self.api.messages.sendMessageEventAnswer(**data)

    async def answer_event_hide_keyboard(self, event_data):
        await self.answer_event(event_data)

        await self.api.messages.edit(
            peer_id=self.peer_id,
            conversation_message_id=self.conversation_message_id,
            keyboard=VkKeyboard.get_empty_keyboard()
        )

    async def answer(self, text: str = '', attachments: Union[Attachment] = '', **kwargs):
        await self.send(self.peer_id, text, attachments, **kwargs)

    def __repr__(self):
        return str(self.raw)
