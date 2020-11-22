class DatabaseConfig:
    __slots__ = ('driver', 'host', 'name', 'user', 'password', 'port')

    def __init__(self, driver: str, host: str, name: str, password: str, port: int):
        self.driver = driver or 'psql'
        self.host = host or 'localhost'
        self.name = name
        self.password = password
        self.port = port or 5432
