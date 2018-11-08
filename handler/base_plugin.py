class BasePlugin:
    __slots__ = ('bot', 'handler', 'api', 'name', 'description')

    def __init__(self):
        self.bot = None
        self.api = None
        self.handler = None

        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__

        if not hasattr(self, 'description'):
            self.description = ''

    def set_up(self, bot, api, handler):
        self.bot = bot
        self.api = api
        self.handler = handler

    def pre_init(self):
        pass

    def init(self):
        pass

    async def before_check(self, msg):
        pass

    async def check(self, msg):
        pass

    async def after_check(self, msg):
        pass

    async def before_process(self, msg, plugin):
        pass

    async def process(self, msg):
        pass

    async def after_process(self, msg, plugin, result):
        pass

    async def before_event_check(self, event):
        pass

    async def check_event(self, event):
        pass

    async def before_event(self, event, plugin):
        pass

    async def process_event(self, event):
        pass

    async def after_event(self, event, plugin, result):
        pass
