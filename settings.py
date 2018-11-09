from plugins.cmd import CMD
from plugins.demo_plugin import DemoPlugin
from utils.peewee import PeeweePlugin


class Settings:
    """group auth
    auth = ('group', 'token')
    user auth
    auth = ('group', 'login', 'password')"""

    auth = ('type',)

    scope = 140489887
    app_id = 6746678
    prefixes = ('/',)
    debug = False

    plugins = [
        PeeweePlugin('host', 'name', 'user',
                     'password', 5432,
                     'PostgreSQL'),
        DemoPlugin(prefixes=prefixes),
        CMD(prefixes=prefixes)
    ]
