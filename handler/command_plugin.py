from handler.base_plugin import BasePlugin


class CommandPlugin(BasePlugin):
    def __init__(self, commands, prefixes):
        self.commands = commands
        self.prefixes = prefixes
        super().__init__()

    def check(self, msg):
        for p in self.prefixes:
            if msg.text.startswith(p):
                text = msg.text[len(p):]
                break
        else:
            return False
        for c in self.commands:
            if text.startswith(c):
                msg.meta['full'] = text
                msg.meta['cmd'] = text[:len(c)]
                msg.meta['args'] = text.split()[len(c.split()):len(text.split())]
                return True
        return False
