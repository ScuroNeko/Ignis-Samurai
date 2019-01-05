from handler.command_plugin import CommandPlugin


class Ping(CommandPlugin):
    def __init__(self, prefixes):
        self.commands = ['ping']
        self.prefixes = prefixes
        super().__init__(self.commands, self.prefixes)

    def msg_process(self, msg):
        return msg.answer('Pong!')
