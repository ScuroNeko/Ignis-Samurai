class VKBasePlugin:
    __slots__ = ('name', 'api', 'session', 'handler')

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.api = None
        self.session = None
        self.handler = None

    def set_up(self, api, session, handler):
        self.api = api
        self.session = session
        self.handler = handler

    def pre_init(self) -> None:
        ...

    def init(self) -> None:
        ...

    def post_init(self) -> None:
        ...

    async def pre_check_msg(self, msg) -> None:
        ...

    async def check_msg(self, msg) -> bool:
        return False

    async def post_check_msg(self, msg) -> None:
        ...

    async def pre_process_msg(self, msg) -> None:
        ...

    async def process_msg(self, msg) -> None:
        ...

    async def post_process_msg(self, msg) -> None:
        ...


class VKCommandPlugin(VKBasePlugin):
    def __init__(self, commands, prefixes):
        super().__init__()
        self.commands = commands
        self.prefixes = prefixes

    async def check_msg(self, msg):
        for p in self.prefixes:
            if msg.text.startswith(p):
                text = msg.text[len(p):]
                break
        else:
            return False

        for c in self.commands:
            if text.startswith(c):
                msg.meta['cmd'] = c
                msg.meta['args'] = msg.original_text[len(c)+1+len(p):]
                return True
        return False
