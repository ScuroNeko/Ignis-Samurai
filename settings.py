from plugins.demo.cmd_plugin import CMD
from plugins.control.antiflood import AntifloodPlugin
from plugins.demo.keyboard import KeyboardPlugin
from plugins.demo.vk_functions import VKFunctions
from plugins.demo.db_plugin import DemoPlugin
from utils.peewee import PeeweePlugin


class Settings:
    """group auth
    auth = ('group', 'token')
    user auth
    auth = ('group', 'login', 'password')"""

    auth = ('type',)

    scope = 140489887
    app_id = 6746678
    prefixes = ('/', 'бот ', 'бот, ')
    debug = False

    plugins = [
        PeeweePlugin('host', 'name', 'user',
                     'password', 5432,
                     'PostgreSQL'),
        DemoPlugin(prefixes=prefixes),
        CMD('work', prefixes=prefixes),
        KeyboardPlugin(prefixes=prefixes),
        VKFunctions(),
        AntifloodPlugin()
    ]
