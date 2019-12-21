from plugins.echo import echo


class BaseSettings:
    token = ''
    plugins = ()
    prefixes = (
        '!', '/'
    )
    debug = True
    database = {
        'driver': '',
        'host': '',
        'name': '',
        'user': '',
        'password': '',
        'port': 0
    }


class Settings(BaseSettings):
    plugins = (
        echo,
    )
    token = ''
    debug = False
    database = {
        'driver': '',
        'host': 'localhost',
        'name': 'bot',
        'user': 'root',
        'password': ''
    }
