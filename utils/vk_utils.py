from random import randint


def get_self_id(api):
    return api.groups.getById()[0]['id']


def generate_random_id():
    return randint(-9*99, 9*99)
