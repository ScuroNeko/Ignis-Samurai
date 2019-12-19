import logging


class Logger:
    log = None

    def __init__(self):
        from settings import Settings
        formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d]: %(message)s',
                                      '%H:%M:%S %d.%m.%Y')
        level = logging.DEBUG if Settings.debug else logging.INFO

        Logger.log = logging.Logger('Kurumi Bot', level=level)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler('log.txt')
        file_handler.setFormatter(formatter)

        Logger.log.addHandler(console_handler)
        Logger.log.addHandler(file_handler)

        Logger.log.info('Logger initialized')
