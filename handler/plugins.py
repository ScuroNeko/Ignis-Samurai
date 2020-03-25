import re

from handler.message import Message, MessageArgs
from handler.event import ChatEvent, Event


class MethodWithPriority:
    __slots__ = ('priority', 'method')

    def __init__(self, method, priority):
        self.priority = priority
        self.method = method

    def call(self):
        self.method()


class Plugin:
    __slots__ = ('custom_checker', 'custom_processor',
                 'commands', 'commands_args',
                 'payloads', 'payloads_args',
                 'events', 'chat_events', 'init_methods',
                 'before_process_methods', 'shutdown_methods')

    def __init__(self, custom_checker=None, custom_processor=None):
        self.custom_checker = custom_checker
        self.custom_processor = custom_processor

        self.commands: dict = {}
        self.commands_args: dict = {}

        self.payloads: dict = {}
        self.payloads_args: dict = {}

        self.events: dict = {}
        self.chat_events: dict = {}

        self.init_methods: list = []
        self.before_process_methods: list = []

        self.shutdown_methods: list = []

    def init(self, priority: int = 0):
        def wrapper(f):
            self.init_methods.append(MethodWithPriority(f, priority))
            self.init_methods.sort(key=lambda method: method.priority, reverse=True)
            return f

        return wrapper

    def before_process(self, priority: int = 0):
        def wrapper(f):
            self.before_process_methods.append(MethodWithPriority(f, priority))
            self.before_process_methods.sort(key=lambda method: method.priority, reverse=True)
            return f

        return wrapper

    def on_command(self, *commands, args=''):
        def wrapper(f):
            self.commands_args.update(map(lambda cmd: (cmd, args), commands))
            self.commands.update(map(lambda cmd: (cmd, f), commands))
            return f

        return wrapper

    def on_payload(self, *payloads, args=''):
        def wrapper(f):
            self.payloads_args.update(map(lambda cmd: (cmd, args), payloads))
            self.payloads.update(dict(map(lambda payload: (payload, f), payloads)))
            return f

        return wrapper

    def on_event(self, *events):
        def wrapper(f):
            self.chat_events.update(
                map(lambda event: (event, f), filter(lambda event: event.startswith('chat'), events)))
            self.events.update(map(lambda event: (event, f),
                                   filter(lambda event: not event.startswith('chat'), events)))
            return f

        return wrapper

    def on_shutdown(self, priority: int = 0):
        def wrapper(f):
            self.shutdown_methods.append(MethodWithPriority(f, priority))
            self.shutdown_methods.sort(key=lambda method: method.priority, reverse=True)
            return f

        return wrapper

    async def process_command(self, command: str, msg: Message):
        await self.commands[command](msg)

    async def validate_command_args(self, command: str, cmd_args: tuple) -> (bool, MessageArgs):
        commands_args = self.commands_args
        if command not in commands_args:
            return False, MessageArgs({})

        args = commands_args[command].split()

        if len(cmd_args) < len(tuple(filter(lambda x: '?' not in x, args))):
            return False, None

        args_map = []
        for arg in args:
            name, arg_type = arg.split(':')
            if name.endswith('?'):
                name = name[:-1]

            arg_type = arg_type.replace('str', r'.').replace('int', r'\d')
            args_map.append((name, re.compile(arg_type)))

        args = dict()

        for index in range(len(cmd_args)):
            name, expression = args_map[index]
            if not expression.match(cmd_args[index]):
                return False, None
            args.update({name: cmd_args[index]})

        return True, MessageArgs(args)

    async def process_command_with_args(self, command: str, msg: Message, args: MessageArgs):
        await self.commands[command](msg, args)

    async def process_payload(self, payload: str, msg: Message):
        await self.payloads[payload](msg)

    async def process_chat_event(self, event_type: str, event: ChatEvent, msg: Message):
        await self.chat_events[event_type](event, msg)

    async def process_event(self, event_type: str, event: Event):
        await self.events[event_type](event)
