from handler.base_plugin import BasePlugin


class CommandPlugin(BasePlugin):
    def __init__(self, commands, prefixes):
        super().__init__()
        self.commands = commands if commands else []
        self.prefixes = prefixes if prefixes else []

    async def check(self, msg):
        cmd = msg.text.split(sep='] ')[::-1][0]
        for p in self.prefixes:
            if cmd.startswith(p):
                cmd = cmd[1:]
        for c in self.commands:
            if cmd.startswith(c):
                msg.meta['cmd'] = cmd
                return True
        return False

    async def process(self, msg):
        pass
