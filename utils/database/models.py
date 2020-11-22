from peewee import Model, IntegerField, BigIntegerField, DecimalField, TextField, ForeignKeyField, DateTimeField, \
    BooleanField, CompositeKey, CharField

from utils.database.database import Database


class Models:
    group = None
    work = None
    user = None
    fraction = None
    reports = None
    auto = None
    business = None
    maid = None
    miner = None
    fraction_member = None

    @staticmethod
    def init():
        class BaseModel(Model):
            class Meta:
                database = Database.db

        class Groups(BaseModel):
            id = IntegerField()
            name = TextField()
            is_vip = BooleanField()
            is_admin = BooleanField()
            multiplier = DecimalField()
            sale = DecimalField()

        class Works(BaseModel):
            id = IntegerField()
            name = TextField()
            required_lvl = IntegerField()
            money_income = DecimalField()
            exp_income = DecimalField()

        class Fractions(BaseModel):
            id = IntegerField()
            name = TextField()
            owner_id = IntegerField()
            money = DecimalField()
            exp = IntegerField()
            level = IntegerField()

        class Auto(BaseModel):
            id = IntegerField()
            name = TextField()
            price = DecimalField()

            class Meta:
                table_name = 'shop_auto'

        class Business(BaseModel):
            id = IntegerField()
            name = TextField()
            price = DecimalField()
            income = DecimalField()

            class Meta:
                table_name = 'shop_business'

        class Maid(BaseModel):
            id = IntegerField()
            name = TextField()
            price = DecimalField()
            income = DecimalField()

            class Meta:
                table_name = 'shop_maid'

        class Miner(BaseModel):
            id = IntegerField()
            name = TextField()
            price = DecimalField()
            income = DecimalField()

            class Meta:
                table_name = 'shop_miner'

        class Users(BaseModel):
            id = IntegerField()
            user_id = BigIntegerField()

            name = TextField()
            greeting = TextField()
            pair = IntegerField()
            donat = IntegerField()

            balance = DecimalField(default=10000, max_digits=20)
            invested = DecimalField(default=0, max_digits=20)
            btc = DecimalField(default=0, max_digits=20, decimal_places=6)
            level = IntegerField()
            exp = DecimalField(default=0)

            group = ForeignKeyField(Groups)
            fraction = ForeignKeyField(Fractions, null=True, lazy_load=True)

            work = ForeignKeyField(Works)
            work_time = DateTimeField()

            income_time = DateTimeField()

            auto = ForeignKeyField(Auto)
            business = ForeignKeyField(Business)
            maid = ForeignKeyField(Maid)
            miner = ForeignKeyField(Miner)

            subscribed = BooleanField()

        class Reports(BaseModel):
            id = IntegerField(unique=True, null=False, primary_key=True)
            text = TextField(null=False)
            admin_answer = TextField(null=True)
            from_id = BigIntegerField(null=False)
            date = DateTimeField()
            status = CharField(null=False)
            attachments = TextField(null=True)

        class FractionMember(BaseModel):
            fraction = ForeignKeyField(Fractions)
            user = ForeignKeyField(Users)
            is_moderator = BooleanField()
            is_admin = BooleanField()

            class Meta:
                table_name = 'fraction_member'
                primary_key = CompositeKey('fraction', 'user')

        Models.group = Groups
        Models.work = Works
        Models.user = Users
        Models.fraction = Fractions
        Models.reports = Reports
        Models.auto = Auto
        Models.business = Business
        Models.maid = Maid
        Models.miner = Miner
        Models.fraction_member = FractionMember
