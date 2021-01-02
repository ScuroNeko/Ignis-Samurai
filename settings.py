class BaseSettings:
    token = ''
    sentry_dsn = ''
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
    sentry_dsn = ''
    debug = False
    database = {
        'driver': '',
        'host': 'localhost',
        'name': 'bot',
        'user': 'root',
        'password': ''
    }
