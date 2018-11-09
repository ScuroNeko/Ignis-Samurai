from handler.command_plugin import CommandPlugin


class CMD(CommandPlugin):
    def __init__(self, prefixes):
        self.commands = ['work']
        super().__init__(self.commands, prefixes)

    async def process(self, msg):
        return await msg.answer('I work!')
