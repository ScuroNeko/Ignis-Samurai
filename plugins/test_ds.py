from discord import Embed

from handler.ds.ds_command_plugin import DSCommandPlugin


class TestDSPlugin(DSCommandPlugin):
    def __init__(self, prefixes):
        """
        Плагин, который будет работать только в дискорде
        :param prefixes:
        """
        self.commands = ['test']
        super().__init__(self.commands, prefixes)

    async def msg_process(self, msg):
        print(msg.text)
        embed = Embed(colour=0x00ffff, title='Привет! Я тестовое название с ссылкой!',
                      description='Привет! А я тестовое описание с ссылкой!',
                      url='https://github.com/Nix1304/Ignis-Samurai')
        embed.set_author(name='Nix13#5803', url='https://vk.com/nix13',
                         icon_url='https://pp.userapi.com/c850424/v850424044/19381/wOBckm-w0V4.jpg')
        embed.add_field(name='Имя канала', value=msg.channel.name)
        embed.add_field(name='Имя сервера', value=msg.server.name)
        embed.set_footer(text='Я подвал.')
        return await msg.answer(embed=embed)
