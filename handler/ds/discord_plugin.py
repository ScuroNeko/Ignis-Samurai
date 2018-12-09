class DiscordPlugin:
    __slots__ = ('bot', 'handler', 'client', 'name', 'description')

    def __init__(self):
        self.bot = None
        self.client = None
        self.handler = None

        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__

        if not hasattr(self, 'description'):
            self.description = ''

    def set_up(self, bot, client, handler):
        self.bot = bot
        self.client = client
        self.handler = handler

    def init(self):
        """ First thing in plugin(after __init__())
        """
        pass

    async def check(self, msg) -> bool:
        """ Method execute for check if before_check() return True
        :param msg: Message class
        :return: True if plugin needs process
        """
        pass

    async def msg_process(self, msg) -> None:
        """ Method for message process
        :param msg: Message class
        """
        pass

    def stop(self):
        pass
