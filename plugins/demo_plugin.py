import peewee

from handler.base_plugin import BasePlugin


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
            pair = peewee.BigIntegerField(default=0)
            balance = peewee.DecimalField(default=10000, max_digits=999, decimal_places=0)

            class Meta:
                database = self.pwmanager.database

        DemoPlugin.user = EconomyUser

    async def check(self, msg):
        cmd = msg.text.split(sep='] ')[::-1][0]
        for p in self.prefixes:
            if cmd.startswith(p):
                cmd = cmd[1:]
        for c in self.commands:
            if cmd.startswith(c):
                msg.meta['cmd'] = cmd
                return True
        return False

    async def process(self, msg):
        if msg.meta['cmd'] == 'профиль':
            user = await self.pwmanager.get(DemoPlugin.user, user_id=msg.user_id)
            balance = user.balance
            user = self.api.users.get(user_ids=msg.user_id)[0]
            return await msg.answer('Hi, {} {}!\n'
                                    'Your balance: {}'.format(user['first_name'], user['last_name'], balance),
                                    ['photo136950703_456252183', 'photo136950703_456252882'])

    async def check_event(self, event):
        if event.action == 'chat_title_update':
            return True
        return False

    async def process_event(self, event):
        user = self.api.users.get(user_ids=event.user_id)[0]
        return self.api.messages.send(peer_id=event.peer_id,
                                      message='{} {} поменял навание беседы.'.format(user['first_name'],
                                                                                     user['last_name']))
