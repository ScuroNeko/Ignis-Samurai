class MessageHandler:
    def __init__(self, bot, api):
        self.api = api
        self.bot = bot
        self.plugins = []
        for plugin in bot.settings.plugins:
            plugin.set_up(self.bot, self.api, self)
            self.plugins.append(plugin)

    def initiate(self):
        for plugin in self.plugins:
            self.bot.logger.debug('Pre-init: {}'.format(plugin.name))
            plugin.pre_init()

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
            if await p.before_process(msg, plugin) is False:
                return
        result = await plugin.process(msg)
        for p in self.plugins:
            await p.after_process(msg, plugin, result)
        return result

    async def process_event(self, event):
        for p in self.plugins:
            if await p.before_event_check(event) is False:
                self.bot.logger.debug(f'Event {event} cancelled with {p.name}')
                return
        for p in self.plugins:
            if await p.check_event(event):
                if await self.process_event_with_plugin(event, p) is not False:
                    self.bot.logger.debug(f'Finished with event ({event}) on {p.name}')
                    break
        else:
            self.bot.logger.debug(f'Processed event ({event})')

    async def process_event_with_plugin(self, event, plugin):
        for p in self.plugins:
            if await p.before_event(event, plugin) is False:
                return
        result = await plugin.process_event(event)
        for p in self.plugins:
            await p.after_event(event, plugin, result)
        return result

    def stop(self):
        for plugin in self.plugins:
            self.bot.logger.debug(f'Stopping plugin: {plugin.name}')
            plugin.stop()
