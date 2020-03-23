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
