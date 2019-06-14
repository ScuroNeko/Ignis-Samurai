class TelegramBasePlugin:
    __slots__ = ('name', 'bot')

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.bot = None

    def set_up(self, bot):
        self.bot = bot

    def pre_init(self) -> None:
        ...

    def init(self) -> None:
        ...

    def post_init(self) -> None:
        ...

    async def pre_check_msg(self, msg):
        ...

    async def check_msg(self, msg):
        return False

    async def post_check_msg(self, msg):
        ...

    async def pre_process_msg(self, msg):
        ...

    async def process_msg(self, msg):
        ...

    async def post_process_msg(self, msg):
        ...
