class BaseHandler:
    __slots__ = ('name',)

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__

    def listen(self, settings):
        """
        Тут необходимо получать запросы от API
        :return: None
        """
        ...
