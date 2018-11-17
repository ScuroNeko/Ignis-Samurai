import peewee

from handler.base_plugin import BasePlugin
from utils.utils import get_user_name


class DemoPlugin(BasePlugin):
    user = None

    def __init__(self, prefixes=None):
        self.commands = ['профиль', ]
        self.prefixes = prefixes
        self.pwmanager = None
        super().__init__()

    def init(self):
        if self.pwmanager is None:
            raise ValueError('PeeWee plugin not loaded! Check settings and try again!')

        class EconomyUser(peewee.Model):
            user_id = peewee.BigIntegerField(primary_key=True, unique=True)
            balance = peewee.DecimalField(default=10000, max_digits=999, decimal_places=0)

            class Meta:
                database = self.pwmanager.database

        DemoPlugin.user = EconomyUser

    async def check(self, msg):
        cmd = msg.text
        for p in self.prefixes:
            if cmd.startswith(p):
                cmd = cmd[len(p):]
        for c in self.commands:
            if cmd.startswith(c):
                msg.meta['cmd'] = cmd
                return True
        return False

    async def process(self, msg):
        if msg.meta['cmd'] == 'профиль':
            user = await self.pwmanager.get(DemoPlugin.user, user_id=msg.user_id)
            balance = user.balance
            return await msg.answer('Hi, {}!\n'
                                    'Your balance: {}'.format(get_user_name(self.api, user.user_id), balance),
                                    ['photo136950703_456252183', 'photo136950703_456252882'])
