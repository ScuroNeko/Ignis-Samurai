from json import JSONEncoder


class EnumEncoder(JSONEncoder):
    def default(self, obj):
        return obj.value
