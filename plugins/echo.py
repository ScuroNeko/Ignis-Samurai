from handler.message import Message
from handler.plugins import Plugin
from utils.database import Database
from utils.logger import Logger

echo = Plugin()


@echo.init(10)
def first_init():
    Logger.log.info('1st init')


@echo.init(5)
def second_init():
    Logger.log.info('2nd init')


@echo.on_command('ping', 'dick')
@echo.on_payload('ping')
async def ping(msg: Message):
    print(Database.db)
    return msg.answer('Pong!')
