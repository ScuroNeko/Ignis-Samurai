import peewee

from handler.command_plugin import CommandPlugin
from utils.data import VKMessage


class Ping(CommandPlugin):
    def __init__(self, prefixes):
        self.commands = ['ping']
        self.prefixes = prefixes
        self.db = None
        self.user = None
        super().__init__(self.commands, self.prefixes)

    def init(self):
        class User(peewee.Model):
            user_id = peewee.BigIntegerField()
            balance = peewee.DecimalField(default=1000)

            class Meta:
                database = self.db

        self.user = User

    def msg_process(self, msg):
        if isinstance(msg, VKMessage):
            user = self.user.get(user_id=msg.user_id)
            balance = str(user.balance)
        else:
            balance = 'N/A'
        return msg.answer('Your balance: ' + balance)
