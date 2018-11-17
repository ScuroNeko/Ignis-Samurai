import asyncio

from handler.base_plugin import BasePlugin
from utils import utils


class VKFunctions(BasePlugin):
    def __init__(self):
        super().__init__()

    def init(self):
        asyncio.ensure_future(self.work())

    async def work(self):
        while True:
            if self.api.groups.getOnlineStatus(group_id=utils.get_self_id(self.api))['status'] != 'online':
                self.api.groups.enableOnline(group_id=utils.get_self_id(self.api))
            await asyncio.sleep(1)
