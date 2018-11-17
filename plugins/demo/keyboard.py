from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from handler.command_plugin import CommandPlugin


class KeyboardPlugin(CommandPlugin):
    def __init__(self, prefixes):
        self.commands = ['клавиатура']
        super().__init__(self.commands, prefixes)

    async def process(self, msg):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Белая 1', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Белая 2', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Синяя 1', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Синяя 2', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Синяя 3', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Красная 1', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Красная 2', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Зеленая 1', color=VkKeyboardColor.POSITIVE)
        return await msg.answer('Клавиатура показана!', keyboard=keyboard)
