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

    def before_check(self, msg) -> bool:
        """ Method execute before check
        :param msg: Message class
        :return: True if plugin needs check
        """
        pass

    def check(self, msg) -> bool:
        """ Method execute for check if before_check() return True
        :param msg: Message class
        :return: True if plugin needs process
        """
        pass

    def after_check(self, msg) -> None:
        """ Method execute after check if check() return True
        :param msg: Message class
        """
        pass

    def before_msg_process(self, msg) -> None:
        """ Method execute before message process
        :param msg: Message class
        """
        pass

    def msg_process(self, msg) -> None:
        """ Method for message process
        :param msg: Message class
        """
        pass

    def after_msg_process(self, msg) -> None:
        """ Method execute after message process
        :param msg: Message class
        """
        pass

    def stop(self):
        pass
