from handler.command_plugin import CommandPlugin


class CMD(CommandPlugin):
    def __init__(self, *commands, prefixes):
        super().__init__(commands, prefixes)

    async def process(self, msg):
        return await msg.answer('I work!')
