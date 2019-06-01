class TelegramBasePlugin:
    __slots__ = ('name', 'bot')

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.bot = None

    def set_up(self, bot):
        self.bot = bot

    def init(self):
        ...

    def check_msg(self, msg) -> bool:
        ...

    def process_msg(self, msg) -> None:
        ...


class TelegramCommandPlugin(TelegramBasePlugin):
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
                msg.meta['cmd'] = c
                msg.meta['args'] = text[len(c):].split
                return True

        return False
