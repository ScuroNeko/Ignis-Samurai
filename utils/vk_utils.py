import io
from random import randint

import aiohttp


def get_self_id(api):
    return api.groups.getById()[0]['id']


def generate_random_id():
    return randint(-9 ** 99, 9 ** 99)


def get_user_name(id, api, name_case='nom'):
    user = api.users.get(user_ids=id, name_case=name_case)[0]
    return f'{user["first_name"]} {user["last_name"]}'


async def reupload_attachments(attachments, upload):
    new_attachments = []
    for a in attachments:
        t = a['type']
        if t != 'photo':
            continue
        url = a[t]['sizes'][-1]['url']

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                file = io.BytesIO(await response.read())
                attachment = upload.photo_messages(file)[0]
                new_attachments.append(f'photo{attachment["owner_id"]}_{attachment["id"]}')
    return new_attachments
