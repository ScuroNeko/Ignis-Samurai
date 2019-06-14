import peewee
from peewee import Model

from vk.vk_plugin import VKCommandPlugin


class BalancePlugin(VKCommandPlugin):
    def __init__(self, prefixes):
        self.user = None
        self.db = None
        super().__init__(['balance'], prefixes)

    def init(self):
        if self.db is None:
            raise ValueError('PeeWee plugin not loaded! Check settings and try again!')

        class User(Model):
            user_id = peewee.BigIntegerField(primary_key=True, unique=True)
            balance = peewee.DecimalField(999, 0)

            class Meta:
                database = self.db.database

        self.user = User

    async def process_msg(self, msg):
        user = await self.db.get(self.user, user_id=msg.user_id)
        return msg.answer(user.balance)
