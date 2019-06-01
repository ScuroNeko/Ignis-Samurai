class VKBasePlugin:
    __slots__ = ('name', 'api', 'session')

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.api = None
        self.session = None

    def set_up(self, session):
        self.session = session
        self.api = session.get_api()

    def init(self):
        ...

    def check_msg(self, msg) -> bool:
        ...

    def process_msg(self, msg) -> None:
        ...


class VKCommandPlugin(VKBasePlugin):
    def __init__(self, prefixes, commands):
        super().__init__()
        self.prefixes = prefixes
        self.commands = commands

    def check_msg(self, msg):
        text = ''
        for p in self.prefixes:
            if msg.text.startswith(p):
                text = msg.text[len(p):]
                if text.startswith(' '):
                    text = msg.text[1:]

        for c in self.commands:
            if text.startswith(c):
                return True
            break

        return False
