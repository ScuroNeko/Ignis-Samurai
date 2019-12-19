from plugins.echo import echo


class BaseSettings:
    token = ''
    plugins = ()
    prefixes = (
        '!', '/'
    )
    debug = True


class Settings(BaseSettings):
    plugins = (
        echo,
    )
    token = ''
    debug = False
