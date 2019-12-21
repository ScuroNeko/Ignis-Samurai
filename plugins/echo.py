from handler.event import ChatEvent, Event
from handler.message import Message
from handler.plugins import Plugin
from utils.database.models import Models
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
    user, c = Models.user.get_or_create(user_id=msg.from_id)
    return msg.answer(f'ID: {user.id}\n'
                      f'Баланс: {user.balance}$')


@echo.on_event('chat_title_update')
async def notify_chat_title_update(event: ChatEvent, msg: Message):
    msg.answer(f'Название было изменено на {event.text}')


@echo.on_event('wall_reply_new')
async def on_wall_comment(event: Event):
    # Тут мы можем делать все что угодно, используя event.api
    print(event.raw)
