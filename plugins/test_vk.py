from vk.vk_handler import VKCommandPlugin


class TestVK(VKCommandPlugin):
    def __init__(self, prefixes, commands):
        super().__init__(prefixes, commands)

    def process_msg(self, msg):
        msg.answer('XYU')
