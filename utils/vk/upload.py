from aiohttp import ClientSession, FormData

from utils.vk.vk import VK, VkApiMethod


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

    async def photo(self, photos, album_id,
                    latitude=None, longitude=None, caption=None, description=None,
                    group_id=None):

        values = {'album_id': album_id}

        if group_id:
            values['group_id'] = group_id

        url = self.vk.photos.getUploadServer(**values)['upload_url']

        with FilesOpener(photos) as photo_files:
            data = FormData()
            for file in photo_files:
                data.add_field(file[0], file[1][1], filename=file[1][0])
            async with ClientSession() as session, session.post(url, data=data) as r:
                response = await r.json(content_type='text/html')

        if 'album_id' not in response:
            response['album_id'] = response['aid']

        response.update({
            'latitude': latitude,
            'longitude': longitude,
            'caption': caption,
            'description': description
        })

        values.update(response)

        return self.vk.photos.save(**values)

    async def photo_messages(self, photos, peer_id=None):
        url = (await self.vk.photos.getMessagesUploadServer(peer_id=peer_id))['upload_url']

        with FilesOpener(photos) as photo_files:
            data = FormData()
            for file in photo_files:
                data.add_field(file[0], file[1][1], filename=file[1][0])
            async with ClientSession() as session, session.post(url, data=data) as r:
                response = await r.json(content_type='text/html')
        return await self.vk.photos.saveMessagesPhoto(**response)


class FilesOpener(object):
    def __init__(self, paths, key_format='file{}'):
        if not isinstance(paths, list):
            paths = [paths]

        self.paths = paths
        self.key_format = key_format
        self.opened_files = []

    def __enter__(self):
        return self.open_files()

    def __exit__(self, type, value, traceback):
        self.close_files()

    def open_files(self):
        self.close_files()

        files = []

        for x, file in enumerate(self.paths):
            if hasattr(file, 'read'):
                f = file

                if hasattr(file, 'name'):
                    filename = file.name
                else:
                    filename = '.jpg'
            else:
                filename = file
                f = open(filename, 'rb')
                self.opened_files.append(f)

            ext = filename.split('.')[-1]
            files.append(
                (self.key_format.format(x), ('file{}.{}'.format(x, ext), f))
            )

        return files

    def close_files(self):
        for f in self.opened_files:
            f.close()

        self.opened_files = []
