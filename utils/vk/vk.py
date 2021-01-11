import asyncio
from time import time
from typing import Union

from aiohttp import ClientSession, FormData


class VkToken:
    __slots__ = (
        'cur_requests', 'max_rps',
        '__token', '__last_req'
    )

    def __init__(self, token):
        self.cur_requests = 0
        self.max_rps = 20
        self.__token = token
        self.__last_req = 0

    def __call__(self):
        if self.cur_requests >= self.max_rps:
            raise TypeError('too many requests')
        self.cur_requests += 1
        self.__last_req = int(time())
        if self.__last_req < int(time()):
            self.cur_requests = 0
        return self.__token


class VkTokenProvider:
    __slots__ = (
        'tokens',
    )

    def __init__(self, tokens: (Union[VkToken], VkToken)):
        if type(tokens) == str:
            self.tokens = [VkToken(tokens)]
        else:
            self.tokens = [VkToken(t) for t in tokens]

    def obtain_token(self):
        for t in self.tokens:
            if t.cur_requests < t.max_rps:
                return t()
        else:
            raise ValueError('no free tokens!')


class VK:
    __slots__ = (
        'token_provider',
        'v', 'session'
    )

    def __init__(self, tokens: (str, list, tuple, set, frozenset), v='5.126'):
        self.token_provider = VkTokenProvider(tokens)
        self.v = v
        self.session = ClientSession()

    def shutdown(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    async def call_method(self, method, **params):
        params.update({'v': self.v})

        params.update({'access_token': self.token_provider.obtain_token()})

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
