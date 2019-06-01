from vk.vk_plugin import VKCommandPlugin


class TestVK(VKCommandPlugin):
    def __init__(self, prefixes, ):
        self.commands = ['xyu']
        super().__init__(prefixes, self.commands)

    def process_msg(self, msg) -> None:
        return msg.answer('XYU')
