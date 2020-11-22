class BaseSettings:
    token = ''
    plugins = []
    prefixes = [
        '!', '/'
    ]
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
    token = ''
    debug = True
    sentry_dsn = ''
    database = {
        'driver': '',
        'host': 'localhost',
        'name': 'bot',
        'user': 'root',
        'password': ''
    }
