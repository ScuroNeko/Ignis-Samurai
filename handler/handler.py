from handler.ds.discord_plugin import DiscordPlugin
from handler.vk.vk_plugin import VKPlugin


class VkHandler:
    def __init__(self, api, bot):
        self.api = api
        self.bot = bot
        self.plugins = []
        for plugin in bot.settings.plugins:
            if isinstance(plugin, VKPlugin):
                plugin.set_up(self.bot, self.api, self)
                self.plugins.append(plugin)

    def initiate(self):
        for plugin in self.plugins:
            self.bot.logger.debug('Init: {}'.format(plugin.name))
            plugin.init()

    async def process(self, msg):
        for p in self.plugins:
            if await p.before_check(msg) is False:
                return
        for p in self.plugins:
            if await p.check(msg):
                await p.after_check(msg)
                if await self.process_with_plugin(msg, p) is not False:
                    self.bot.logger.debug(f'Finished with message ({msg.msg_id}) on {p.name}')
                    break
        else:
            self.bot.logger.debug(f'Processed message ({msg.msg_id})')

    async def process_with_plugin(self, msg, plugin):
        for p in self.plugins:
            if await p.before_msg_process(msg, plugin) is False:
                return
        result = await plugin.msg_process(msg)
        return result

    def stop(self):
        for plugin in self.plugins:
            self.bot.logger.debug(f'Stopping plugin: {plugin.name}')
            plugin.stop()


class DiscordHandler:
    def __init__(self, client, bot):
        self.client = client
        self.bot = bot
        self.plugins = []
        for plugin in bot.settings.plugins:
            if isinstance(plugin, DiscordPlugin):
                plugin.set_up(self.bot, self.client, self)
                self.plugins.append(plugin)

    def initiate(self):
        for plugin in self.plugins:
            self.bot.logger.debug('Init: {}'.format(plugin.name))
            plugin.init()

    async def process(self, msg):
        for p in self.plugins:
            if await p.check(msg) and await self.process_with_plugin(msg, p) is not False:
                self.bot.logger.debug(f'Finished with message ({msg.id}) on {p.name}')
                break
        else:
            self.bot.logger.debug(f'Processed message ({msg.id})')

    async def process_with_plugin(self, msg, plugin):
        result = await plugin.msg_process(msg)
        return result

    def stop(self):
        for plugin in self.plugins:
            self.bot.logger.debug(f'Stopping plugin: {plugin.name}')
            plugin.stop()
