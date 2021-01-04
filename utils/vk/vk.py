import asyncio

from aiohttp import ClientSession, FormData


class VK:
    def __init__(self, tokens: (str, list, tuple, set, frozenset), v='5.126'):
        self.tokens = tokens
        self.v = v
        self.session = ClientSession()

    def shutdown(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    async def call_method(self, method, **params):
        params.update({'v': self.v})

        if type(self.tokens) is str:
            params.update({'access_token': self.tokens})

        async with self.session.post(
                f'https://api.vk.com/method/{method}',
                data=FormData(params)
        ) as res:
            j = await res.json()

            if 'error' in j:
                error = j['error']
                raise VKApiException(error['error_msg'], error['error_code'])

            if 'response' in j:
                return j['response']

            return j

    def get_api(self):
        return VkApiMethod(self)


class VkApiMethod(object):
    __slots__ = ('_vk', '_method')

    def __init__(self, vk, method=None):
        self._vk: VK = vk
        self._method = method

    def __getattr__(self, method):
        if '_' in method:
            m = method.split('_')
            method = m[0] + ''.join(i.title() for i in m[1:])

        return VkApiMethod(
            self._vk,
            (self._method + '.' if self._method else '') + method
        )

    async def __call__(self, **kwargs):
        return await self._vk.call_method(self._method, **kwargs)


class VKApiException(Exception):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code
