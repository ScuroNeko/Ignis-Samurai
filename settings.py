from plugins.ping import Ping
from plugins.test_vk import TestPlugin
from plugins.test_ds import TestDSPlugin
from utils.peewee import PeeweePlugin


class Settings:
    """Вы должны оставить только один метод авторизации для ВК. Например
    >>> auth = (('vk_group', 'token'),
    >>>         ('ds_bot', 'token'))
    """

    # 100% работает.
    auth = (('vk_group', 'token'),
            ('ds_bot', 'token'))

    scope = 1073741823
    app_id = 6746678
    debug = True
    prefixes = ('/', 'бот ', 'бот, ')

    plugins = [
        PeeweePlugin('host', 'name', 'user',
                     'password', 5432,
                     'PostgreSQL'),
        Ping(prefixes),
        TestPlugin(prefixes),
        TestDSPlugin(prefixes)
    ]
