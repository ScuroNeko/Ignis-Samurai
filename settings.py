from plugins.demo_plugin import DemoPlugin
from utils.peewee import PeeweePlugin


class Settings:
    """group auth
    auth = ('group', 'token')"""
    """user auth
    auth = ('group', 'login', 'password')"""

    auth = ('group', )

    scope = 140489887
    app_id = 6401748
    prefixes = ('/',)
    debug = 1

    plugins = [
        PeeweePlugin('host', 'name', 'user',
                     'password', 5432,
                     'PostgreSQL'),
        DemoPlugin(prefixes=prefixes)
    ]
