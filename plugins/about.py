from vk.vk_plugin import VKCommandPlugin


class About(VKCommandPlugin):
    def __init__(self, prefixes):
        super().__init__(['about', 'о боте'], prefixes)

    async def process_msg(self, msg) -> None:
        return msg.answer('Бот написан на ядре Ignis Samurai V4.0\n'
                          'Автор - https://vk.com/nikitagorshok')
