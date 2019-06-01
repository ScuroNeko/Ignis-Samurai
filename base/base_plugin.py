class BasePlugin:
    __slots__ = ('name', 'tg', 'vk', 'db', 'vk_handler', 'tg_handler')

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.tg = None
        self.vk = None
        self.db = None

    def set_up(self, tg_bot, vk_session):
        self.tg = tg_bot
        self.vk = vk_session

    def init(self):
        ...

    def check_msg(self, msg) -> bool:
        ...

    def process_msg(self, msg) -> None:
        ...


class CommandPlugin(BasePlugin):
    def __init__(self, prefixes, commands):
        super().__init__()
        self.commands = commands
        self.prefixes = prefixes

    def check_msg(self, msg) -> bool:
        text = ''
        for p in self.prefixes:
            if msg.text.startswith(p):
                text = msg.text[len(p):]
                while text.startswith(' '):
                    text = msg.text[1:]
                break

        for c in self.commands:
            if text.startswith(c):
                msg.meta['cmd'] = c
                msg.meta['args'] = text[len(c):].split()
                return True
        return False
