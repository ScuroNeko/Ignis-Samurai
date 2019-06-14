from vk.vk_plugin import VKCommandPlugin


class Echo(VKCommandPlugin):
    def __init__(self, prefixes):
        super().__init__(['echo'], prefixes)

    async def process_msg(self, msg):
        return msg.answer(msg.meta['args'])
