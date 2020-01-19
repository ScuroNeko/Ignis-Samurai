import json

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


class Message:
    def __init__(self, session, api, raw: dict):
        self.session = session
        self.api = api
        self.raw: dict = raw

        self.id: int = self.raw['id']
        self.date: int = self.raw['date']

        self.peer_id: int = self.raw['peer_id']
        self.from_id: int = self.raw['from_id']

        self.original_text: str = self.raw['text']
        self.text: str = self.original_text.lower()
        
        self.attachments: list = self.raw['attachments']

        self.payload: dict = json.loads(self.raw.get('payload', '{}'))

        self.forwarded_messages: list = self.raw.get('fwd_messages', [])
        self.reply_message = Message(self.session, self.api, self.raw['reply_message']) \
            if 'reply_message' in self.raw else None

        self.meta: dict = {}

    def answer(self, text: str = '', attachments: (str, list, tuple, set, frozenset) = '', **kwargs):
        data = kwargs.copy()
        data.update({
            'peer_id': self.peer_id,
            'random_id': generate_random_id()
        })

        if text:
            data.update({'message': text})
        if attachments:
            if type(attachments) == str:
                data.update({'attachment': attachments})
            else:
                data.update({'attachment': ','.join(attachments)})
        self.api.messages.send(**data)
