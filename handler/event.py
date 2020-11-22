from utils.vk_utils import generate_random_id


class ChatEvent:
    __slots__ = ('session', 'api', 'raw', 'type', 'member_id', 'text', 'photo')

    def __init__(self, session, api, raw: dict):
        self.session = session
        self.api = api
        self.raw: dict = raw

        self.type: str = self.raw.get('type', '')
        self.member_id: int = self.raw.get('member_id', 0)
        self.text: str = self.raw.get('text', '')
        self.photo: dict = self.raw.get('photo', {})


class Event:
    __slots__ = ('session', 'api', 'raw', 'type')

    def __init__(self, session, api, raw: dict):
        self.session = session
        self.api = api

        self.raw: dict = raw['object']
        self.type: str = raw['type']

    def send_message(self, target_id, text, attachments: (str, list, tuple, set, frozenset) = '', **kwargs):
        data = kwargs.copy()
        data.update({
            'peer_id': target_id,
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
