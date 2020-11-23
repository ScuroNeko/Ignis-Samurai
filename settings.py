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
    token = '4c64cfe826e81c78f0e7b735e40ba4b942d4e7dc720e6f558e00484f5c29d24a3aa342921efdd27dcf3d7'
    debug = True
    sentry_dsn = ''
    database = {
        'driver': '',
        'host': 'localhost',
        'name': 'bot',
        'user': 'root',
        'password': ''
    }
