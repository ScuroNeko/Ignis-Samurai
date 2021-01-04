import json

from aiohttp import ClientSession, FormData

from handler.message import load_attachments
from utils.vk.vk import VK, VkApiMethod


class JsonParser:
    @staticmethod
    def dumps(data):
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def loads(string):
        return json.loads(string)


class VkUpload(object):
    __slots__ = ('vk',)

    def __init__(self, vk):
        if not isinstance(vk, (VK, VkApiMethod)):
            raise TypeError(
                'The arg should be VK or VkApiMethod instance'
            )

        if isinstance(vk, VkApiMethod):
            self.vk = vk
        else:
            self.vk = vk.get_api()

    async def photo_messages(self, photo, pid=0):
        upload_info = await self.vk.photos.getMessagesUploadServer(peer_id=pid)

        data = FormData()
        data.add_field(
            'photo',
            photo,
            content_type='multipart/form-data',
            filename=f'a.png',
        )

        async with ClientSession() as session, session.post(upload_info['upload_url'], data=data) as response:
            response = await response.text()
            response = json.loads(response)

        photos = await self.vk.photos.saveMessagesPhoto(**response)
        photos = [{'type': 'photo', 'photo': photo} for photo in photos]
        return load_attachments(photos)

    async def doc_message(self, doc, pid):
        upload_info = await self.vk.docs.getMessagesUploadServer(peer_id=pid)

        data = FormData()
        data.add_field(
            'file',
            doc,
            content_type='multipart/form-data',
            filename=f'a.png',
        )

        async with ClientSession() as session, session.post(upload_info['upload_url'], data=data) as response:
            response = await response.text()
            response = json.loads(response)

        return load_attachments([await self.vk.docs.save(**response)])
