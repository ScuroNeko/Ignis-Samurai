from handler.base_plugin import BasePlugin
from handler.ds.discord_plugin import DiscordPlugin
from handler.vk.vk_plugin import VKPlugin
from utils.data import VkMessage


class VkHandler:
    def __init__(self, api, bot):
        self.api = api
        self.bot = bot
        self.plugins = []
        for plugin in bot.settings.plugins:
            if isinstance(plugin, VKPlugin):
                plugin.set_up(self.bot, self.api, self)
                self.plugins.append(plugin)
            elif isinstance(plugin, BasePlugin):
                self.plugins.append(plugin)

    def initiate(self):
        for plugin in self.plugins:
            self.bot.logger.debug('Init: {}'.format(plugin.name))
            plugin.init()

    def process(self, msg):
        for p in self.plugins:
            if p.before_check(msg) is False:
                return
        for p in self.plugins:
            if p.check(msg):
                p.after_check(msg)
                if self.process_with_plugin(msg, p) is not False:
                    self.bot.logger.debug(f'Finished with message ({msg.msg_id}) on {p.name}')
                    break
        else:
            self.bot.logger.debug(f'Processed message ({msg.msg_id})')

    def process_with_plugin(self, msg, plugin):
        for p in self.plugins:
            if p.before_msg_process(msg, plugin) is False:
                return
        result = plugin.msg_process(msg)
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
            elif isinstance(plugin, BasePlugin):
                self.plugins.append(plugin)

    def initiate(self):
        for plugin in self.plugins:
            self.bot.logger.debug('Init: {}'.format(plugin.name))
            plugin.init()

    def process(self, msg):
        for p in self.plugins:
            if p.check(msg) and self.process_with_plugin(msg, p) is not False:
                self.bot.logger.debug(f'Finished with message ({msg.id}) on {p.name}')
                break
        else:
            self.bot.logger.debug(f'Processed message ({msg.id})')

    def process_with_plugin(self, msg, plugin):
        result = plugin.msg_process(msg)
        return result

    def stop(self):
        for plugin in self.plugins:
            self.bot.logger.debug(f'Stopping plugin: {plugin.name}')
            plugin.stop()


class Handler:
    def __init__(self, client, api, bot):
        self.client = client
        self.bot = bot
        self.api = api
        self.plugins = []
        for plugin in bot.settings.plugins:
            if isinstance(plugin, BasePlugin):
                plugin.set_up(self.bot, self.client, self.api, self)
                self.plugins.append(plugin)

    def initiate(self):
        for plugin in self.plugins:
            self.bot.logger.debug('Init: {}'.format(plugin.name))
            plugin.init()

    def process(self, msg):
        for p in self.plugins:
            if p.check(msg) and self.process_with_plugin(msg, p) is not False:
                self.bot.logger.debug(f'Finished with message ({msg.msg_id if isinstance(msg, VkMessage) else msg.id}) on {p.name}')
                break
        else:
            self.bot.logger.debug(f'Processed message ({msg.msg_id if isinstance(msg, VkMessage) else msg.id})')

    def process_with_plugin(self, msg, plugin):
        result = plugin.msg_process(msg)
        return result

    def stop(self):
        for plugin in self.plugins:
            self.bot.logger.debug(f'Stopping plugin: {plugin.name}')
            plugin.stop()
