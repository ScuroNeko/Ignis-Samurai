from plugins.test import TestPlugin
from plugins.test_ds import TestDSPlugin
from utils.peewee import PeeweePlugin


class Settings:
    """Вы должны оставить только один метод авторизации для ВК. Например
    >>> auth = (('vk_group', 'token'),
    >>>         ('ds_bot', 'token'))
    """
    auth = (('vk_group', 'token'),
            ('vk_user', 'login', 'password'),
            ('vk_user', 'token'),
            ('ds_bot', 'token'))

    scope = 1073741823
    app_id = 6746678
    debug = False
    prefixes = ('/', 'бот ', 'бот, ')

    plugins = [
        PeeweePlugin('host', 'name', 'user',
                     'password', 5432,
                     'PostgreSQL'),
        TestPlugin(prefixes),
        TestDSPlugin(prefixes)
    ]
