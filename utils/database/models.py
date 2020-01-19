from peewee import Model, IntegerField, BigIntegerField, DecimalField

from utils.database.database import Database


class Models:
    user = None

    @staticmethod
    def init():
        class BaseModel(Model):
            class Meta:
                database = Database.db

        class User(BaseModel):
            id = IntegerField()
            user_id = BigIntegerField()
            balance = DecimalField(default=10000)

            class Meta:
                table_name = 'users'

        Models.user = User
