import inspect
import re

from handler.event import ChatEvent, Event
from handler.message import Message, MessageArgs


class MethodWithPriority:
    __slots__ = ('priority', 'method')

    def __init__(self, method, priority):
        self.priority = priority
        self.method = method

    def call(self):
        self.method()


class Plugin:
    __slots__ = ('custom_checker', 'custom_processor',
                 'commands', 'commands_args', 'commands_help',
                 'args_help',
                 'vip_commands', 'admin_commands',
                 'payloads', 'payloads_args',
                 'events', 'chat_events', 'init_methods',
                 'before_process_methods', 'shutdown_methods')

    def __init__(self, custom_checker=None, custom_processor=None):
        self.custom_checker = custom_checker
        self.custom_processor = custom_processor

        self.commands: dict = {}
        self.commands_args: dict = {}
        self.commands_help: dict = {}
        self.args_help: dict = {}

        self.vip_commands: list = []
        self.admin_commands: list = []

        self.payloads: dict = {}
        self.payloads_args: dict = {}

        self.events: dict = {}
        self.chat_events: dict = {}

        self.init_methods: list = []
        self.before_process_methods: list = []

        self.shutdown_methods: list = []

    def __repr__(self):
        return str({
            'custom_checker': self.custom_checker,
            'custom_processor': self.custom_processor,

            'commands': list(self.commands.keys()),
            'commands_args': list(self.commands_args.keys()),
            'commands_help': list(self.commands_help.keys()),
            'args_help': list(self.args_help.keys()),

            'vip_commands': self.vip_commands,
            'admin_commands': self.admin_commands,

            'payloads': list(self.payloads.keys()),
            'payloads_args': list(self.payloads_args.keys()),

            'events': list(self.events.keys()),
            'chat_events': list(self.chat_events.keys()),

            'init_methods': self.init_methods,
            'before_process_methods': self.before_process_methods,

            'shutdown_methods': self.shutdown_methods
        })

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

    def on_command(self, *commands, args='', h=tuple(), is_admin: bool = False):
        def wrapper(f):
            self.commands.update(map(lambda cmd: (cmd, f), commands))
            if is_admin:
                self.admin_commands.append(*commands)

            if args:
                self.commands_args.update(map(lambda cmd: (cmd, args), commands))

            if h:
                self.commands_help.update({commands[0]: h[0]})
                if len(h) > 1:
                    self.args_help.update({commands[0]: h[1:]})

            return f

        return wrapper

    def vip_command(self, f):
        for k in self.commands.keys():
            self.vip_commands.append(k)
        return f

    def admin_command(self, f):
        for k in self.commands.keys():
            self.admin_commands.append(k)
        return f

    def on_payload(self, *payloads, args=''):
        def wrapper(f):
            if args:
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

    async def process_command(self, command: str, msg: Message, args: MessageArgs):
        sig = inspect.signature(self.commands[command])
        if len(sig.parameters) == 1:
            await self.commands[command](msg)
        elif len(sig.parameters) == 2:
            await self.commands[command](msg, args)

    def is_vip_command(self, command: str) -> bool:
        return command in self.vip_commands

    def is_admin_command(self, command: str) -> bool:
        return command in self.admin_commands

    async def validate_command_args(self, command: str, cmd_args: tuple) -> (bool, MessageArgs):
        commands_args = self.commands_args
        if command not in commands_args:
            return True, MessageArgs({})

        args = commands_args[command].split()

        if not cmd_args and not tuple(filter(lambda x: '?' not in x, args)):
            return True, MessageArgs({})

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
            if len(args_map) == index:
                break
            name, expression = args_map[index]
            if not expression.match(cmd_args[index]):
                return False, None
            args.update({name: cmd_args[index]})

        return True, MessageArgs(args)

    async def process_payload(self, payload: str, msg: Message):
        await self.payloads[payload](msg)

    async def validate_payload_args(self, payload: str, msg_args: dict) -> (bool, (MessageArgs, None)):
        payloads_args = self.payloads_args
        if payload not in payloads_args:
            return True, None

        args = payloads_args[payload].split()
        if len(msg_args) < len(tuple(filter(lambda x: '?' not in x, args))):
            return False, None

        args_map = []
        for arg in args:
            name, arg_type = arg.split(':')
            if name.endswith('?'):
                name = name[:-1]
            arg_type = arg_type.replace('str', r'.').replace('int', r'\d')
            args_map.append((name, re.compile(arg_type)))

        args = dict()

        for index in range(len(msg_args)):
            name, expression = args_map[index]
            if not expression.match(str(tuple(msg_args.values())[index])):
                return False, None
            args.update({name: tuple(msg_args.values())[index]})

        return True, MessageArgs(args)

    async def process_payload_with_args(self, payload: str, msg: Message, args: MessageArgs):
        await self.payloads[payload](msg, args)

    async def process_chat_event(self, event_type: str, event: ChatEvent, msg: Message):
        await self.chat_events[event_type](event, msg)

    async def process_event(self, event_type: str, event: Event):
        await self.events[event_type](event)
