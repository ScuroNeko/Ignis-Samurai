from handler.event import ChatEvent, Event
from handler.message import Message, MessageArgs
from handler.plugins import Plugin
from utils.database.models import Models
from utils.logger import Logger


async def test_checker(msg: Message, plugin: Plugin):
    if msg.text == 'ping':
        await plugin.process_command('ping', msg)
    return 


# echo = Plugin(custom_checker=test_checker)
echo = Plugin()


@echo.init(10)
def first_init():
    Logger.log.info('1st init')


@echo.init(5)
def second_init():
    Logger.log.info('2nd init')


@echo.on_shutdown()
def on_shutdown():
    Logger.log.info('Shutting down...')


@echo.on_command('ping', args=r'time:int optional?:\d')
async def ping(msg: Message, args: MessageArgs):
    i = []
    for a in args.items():
        i.append(f'{a[0]}: {a[1]}')
    return msg.answer('Полученные аргументы:\n'+'\n'.join(i)+f'\nАргументы, полученные вручную:\ntime: {args.time}\noptional: {args.optional}')


@echo.on_command('dick')
@echo.on_payload('dick')
async def dick(msg: Message):
    user, _ = Models.user.get_or_create(user_id=msg.from_id)
    return msg.answer(f'ID: {user.id}\n'
                      f'Баланс: {user.balance}$')


@echo.on_event('chat_title_update')
async def notify_chat_title_update(event: ChatEvent, msg: Message):
    msg.answer(f'Название было изменено на {event.text}')


@echo.on_event('wall_reply_new')
async def on_wall_comment(event: Event):
    # Тут мы можем делать все что угодно, используя event.api
    print(event.raw)
