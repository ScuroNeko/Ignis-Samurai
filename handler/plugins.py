class InitMethod:
    def __init__(self, method, priority):
        self.priority = priority
        self.method = method

    def init(self):
        self.method()


class Plugin:
    def __init__(self):
        self.commands: dict = {}
        self.payloads: dict = {}

        self.events: dict = {}
        self.chat_events: dict = {}

        self.init_methods: list = []

    def init(self, priority: int = 0):
        def wrapper(f):
            self.init_methods.append(InitMethod(f, priority))
            self.init_methods.sort(key=lambda method: method.priority, reverse=True)
            return f

        return wrapper

    def on_command(self, *commands):
        def wrapper(f):
            self.commands.update(dict(map(lambda cmd: (cmd, f), commands)))
            return f

        return wrapper

    def on_payload(self, *payloads):
        def wrapper(f):
            self.payloads.update(dict(map(lambda payload: (payload, f), payloads)))
            return f

        return wrapper

    def on_event(self, *events):
        def wrapper(f):
            self.chat_events.update(dict(map(lambda event: (event, f),
                                             filter(lambda event: event.startswith('chat'), events))))
            self.events.update(dict(map(lambda event: (event, f),
                                        filter(lambda event: not event.startswith('chat'), events))))
            return f

        return wrapper
