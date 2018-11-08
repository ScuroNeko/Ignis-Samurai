import datetime

import peewee
from playhouse.postgres_ext import ArrayField

from handler.base_plugin import BasePlugin


class Economy(BasePlugin):
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
            btc = peewee.DecimalField(default=0, max_digits=999, decimal_places=0)
            experience = peewee.DecimalField(max_digits=11, decimal_places=0, default=0)
            level = peewee.IntegerField(default=1)
            group = peewee.IntegerField(default=0)
            income_collected = peewee.DateTimeField(default=datetime.datetime.now())
            bonus_collected = peewee.DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=1))
            work = peewee.IntegerField(default=0)
            work_time = peewee.DateTimeField(default=datetime.datetime.now())
            work_cd = peewee.IntegerField(default=4)
            custom_name = peewee.TextField(default='')
            banned = peewee.BooleanField(default=False)
            donate = peewee.IntegerField(default=0)
            quote_config = ArrayField(peewee.TextField)
            country = peewee.TextField(default='RU')
            companies = ArrayField(peewee.TextField)
            income_multiplier = peewee.FloatField(default=1.0)
            reg_date = peewee.DateTimeField(default=datetime.datetime.now())
            uid = peewee.IntegerField(unique=True)
            # Bought
            auto = ArrayField(peewee.TextField)
            house = ArrayField(peewee.TextField)
            business = ArrayField(peewee.TextField)
            maid = ArrayField(peewee.TextField)
            miner = ArrayField(peewee.TextField)
            # Fractions
            fraction = peewee.IntegerField(default=0)
            fraction_cd = peewee.IntegerField(default=0)
            fraction_last_at = peewee.DateTimeField(default=None)
            # Race
            wins = peewee.IntegerField(default=0)
            loses = peewee.IntegerField(default=0)
            # Bank
            invested = peewee.DecimalField(default=0, max_digits=999, decimal_places=0)
            # Auto
            hp = peewee.DecimalField(max_digits=3, default=0, decimal_places=0)
            upgrades = ArrayField(peewee.IntegerField)

            class Meta:
                database = self.pwmanager.database

        Economy.user = EconomyUser

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
            user = self.api.users.get(user_ids=msg.user_id)[0]
            return await msg.answer('Hi, {} {}!'.format(user['first_name'], user['last_name']))
