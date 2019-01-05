from handler.vk.vk_command_plugin import VKCommandPlugin


class TestPlugin(VKCommandPlugin):
    def __init__(self, prefixes):
        """
        Плагин, который будет работать только в ВК
        :param prefixes:
        """
        self.commands = ['test']
        super().__init__(self.commands, prefixes)

    def msg_process(self, msg):
        return msg.answer('TEST')
