import asyncio
import traceback
import json


from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import post
from aiohttp.web import run_app
from sentry_sdk import init as sentry_init, capture_exception

from handler.event import ChatEvent, Event
from handler.message import Message
from settings import Settings
from utils.database.database import Database
from utils.logger import Logger
from utils.utils import get_user_or_none
from utils.vk.longpoll import VKLongPoll, VkBotEventType, VkBotEvent
from utils.vk.vk import VK


class Handler:
    __slots__ = (
        'settings', 'session', 'api', 'plugins', 'middlewares', 'loop',
        'app'
    )

    def __init__(self, settings: Settings, middlewares: list):
        self.settings = settings
        self.session = None
        self.api = None
        self.app = None
        self.plugins = []
        self.middlewares = middlewares
        self.loop = asyncio.get_event_loop()

    def init(self):
        if not self.settings.token:
            Logger.log.error('No access token!')
            exit()
        self.session = VK(self.settings.token)
        self.api = self.session.get_api()

        if self.settings.callback:
            self.app = Application()
            self.app.add_routes([post('/', self.cb)])

        if not self.settings.debug and self.settings.sentry_dsn:
            sentry_init(
                self.settings.sentry_dsn,
                traces_sample_rate=1.0
            )
            Logger.log.info('Sentry initialized!')

        for p in self.settings.plugins:
            for init in p.init_methods:
                Logger.log.debug(f'Init: {p.__class__.__name__}')
                init.call()
            self.plugins.append(p)

    def shutdown(self):
        for p in self.plugins:
            for method in p.shutdown_methods:
                method.call()
        Logger.log.info('Bot has been shutdown!')

    async def check_payload(self, msg: Message):
        payload = msg.payload['command'] if 'command' in msg.payload else ''
        args = msg.payload['args'] if 'args' in msg.payload else []

        for p in self.plugins:
            if p.custom_checker:
                try:
                    for before_process in p.before_process_methods:
                        before_process()
                    await p.custom_checker(msg, p)
                    return True
                except Exception as e:
                    if self.settings.debug:
                        Logger.log.error(traceback.format_exc())
                    else:
                        capture_exception(e)

            if payload in p.payloads.keys():
                try:
                    msg.meta.update({'args': args})

                    for before_process in p.before_process_methods:
                        before_process.call()

                    valid, args = await p.validate_payload_args(payload, args)

                    if not valid:
                        await msg.answer('Неверное количество или тип аргументов!')
                        return False

                    for before_process in p.before_process_methods:
                        before_process.call()

                    if valid and args is not None:
                        await p.process_payload_with_args(payload, msg, args)
                    else:
                        await p.process_payload(payload, msg)
                    return True
                except Exception as e:
                    if self.settings.debug:
                        Logger.log.error(traceback.format_exc())
                    else:
                        capture_exception(e)

            else:
                return False

    async def check_command(self, msg: Message):
        text = msg.text

        for prefix in self.settings.prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
                msg.meta['prefix'] = prefix
                break
        else:
            if msg.is_chat:
                return

        for p in self.plugins:
            if p.custom_checker:
                try:
                    for before_process in p.before_process_methods:
                        before_process()
                    await p.custom_checker(msg, p)
                    return
                except Exception as e:
                    if self.settings.debug:
                        Logger.log.error(traceback.format_exc())
                    else:
                        capture_exception(e)

            for command in p.commands:
                if text.startswith(command):
                    if p.is_vip_command(command):
                        user = get_user_or_none(msg.from_id)
                        if not user or not user.group.is_vip:
                            return msg.answer('Для доступа к этой команде требует VIP доступ!')

                    if p.is_admin_command(command):
                        user = get_user_or_none(msg.from_id)
                        if not user or not user.group.is_admin:
                            return msg.answer('Данная комманда доступна только для администраторов!')
                    try:
                        msg.meta['cmd'] = command
                        args = text[len(command) + 1:].split()
                        msg.meta['args'] = args
                        args_valid, args = await p.validate_command_args(command, args)
                        if not args_valid:
                            return await msg.answer('Неверное количество или тип аргументов!')

                        for before_process in p.before_process_methods:
                            before_process.call()

                        await p.process_command(command, msg, args)
                        return
                    except Exception as e:
                        if self.settings.debug:
                            Logger.log.error(traceback.format_exc())
                        else:
                            capture_exception(e)

    async def check(self, msg: Message):
        db = Database.db

        if db:
            if not db.is_closed():
                Logger.log.debug('Connection reopened!')
            else:
                db.connect(True)
                Logger.log.debug('Connection opened!')
        else:
            Logger.log.debug('No database')

        for m in self.middlewares:
            m(msg)

        if not await self.check_payload(msg):
            await self.check_command(msg)

        if db:
            db.close()
            Logger.log.debug('Connection closed!')

    async def check_event(self, event: (ChatEvent, Event), msg: (Message, None)):
        event_type = event.type

        for plugin in self.plugins:
            if event_type in plugin.chat_events.keys():
                try:
                    for before_process in plugin.before_process_methods:
                        before_process.call()
                    return await plugin.chat_events[event_type](event, msg)
                except Exception as e:
                    if self.settings.debug:
                        Logger.log.error(traceback.format_exc())
                    else:
                        capture_exception(e)

            elif event_type in plugin.events.keys():
                try:
                    for before_process in plugin.before_process_methods:
                        before_process.call()
                    return await plugin.events[event_type](event)
                except Exception as e:
                    if self.settings.debug:
                        Logger.log.error(traceback.format_exc())
                    else:
                        capture_exception(e)

    def run(self):
        if self.settings.callback:
            run_app(self.app, port=self.settings.callback_port)
        try:
            self.loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            self.session.shutdown()

    async def handle_event(self, event):
        if (event.type == VkBotEventType.MESSAGE_NEW and 'action' not in event.obj) or\
                event.type == VkBotEventType.MESSAGE_EVENT:
            msg = Message(self.session, self.api, event.obj)
            await self.check(msg)

        elif event.type == VkBotEventType.MESSAGE_NEW and 'action' in event.obj:
            e = ChatEvent(self.session, self.api, event.obj['action'])
            msg = Message(self.session, self.api, event.obj)
            await self.check_event(e, msg)

        else:
            e = Event(self.session, self.api, event.raw)
            await self.check_event(e, None)

    async def _run(self):
        group = (await self.api.groups.getById())[0]
        Logger.log.info(f'Login as {group["name"]} (https://vk.com/public{group["id"]})')

        lp = VKLongPoll(self.session)
        await lp.init_lp()

        async for event in lp.listen():
            try:
                await self.handle_event(event)
            except Exception as e:
                if self.settings.debug:
                    Logger.log.error(traceback.format_exc())
                else:
                    capture_exception(e)

    async def cb(self, req: Request):
        if not req.body_exists:
            return Response(status=400)

        body = await req.text()
        if not body:
            return Response(status=400)

        body = json.loads(body)
        if body['type'] == 'confirmation':
            return Response(text=self.settings.callback_code, status=200)

        if 'secret' in body:
            if not self.settings.callback_secret:
                Logger.log.error('no callback secret')
                return Response(status=500)
            if self.settings.callback_secret != body['secret']:
                return Response(status=403)

        event = VkBotEvent(body)
        await self.handle_event(event)
        return Response(text='ok')
