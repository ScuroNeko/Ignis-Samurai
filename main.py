# Entry point
from bot import Bot
from plugins.echo import echo
from settings import Settings

bot = Bot(Settings)
bot.add_plugin(echo)
bot.run()
