import asyncio
import json
import logging
import time
from asyncio import Task

import aiohttp as aiohttp
import vk_api
import vk_api.bot_longpoll

from settings import Settings

v = '5.87'


class Bot:
    def __init__(self, settings):
        self.api = None
        self.settings = settings

        # Logging
        self.logger = None
        self.logger_file = None

        # Longpoll data
        self.longpoll_server = ''
        self.longpoll_values = {}
        self.longpoll_request = None

        # Asyncio
        self.main_task = None
        self.loop = asyncio.get_event_loop()

        # Execute methods
        self.init_logger()
        self.auth()
        self.longpoll_run()

    def auth(self):
        try:
            if len(self.settings.auth) == 2:
                self.api = vk_api.VkApi(token=self.settings.auth[1])
            elif len(self.settings.auth) == 3:
                self.api = vk_api.VkApi(login=self.settings.auth[1], password=self.settings.auth[2])
            elif len(self.settings.auth) <= 1:
                self.logger.critical('Token or login/password not set!')
                exit()
            else:
                self.logger.critical('Unexpected auth error!')
                exit()

            self.logger.info('Logged as {}'.format(self.settings.auth[0]))
        except vk_api.ApiError as e:
            self.logger.critical(e)
            exit()

    def init_logger(self):
        formatter = logging.Formatter(fmt='%(filename)s [%(asctime)s] %(levelname)s: %(message)s',
                                      datefmt='%d-%m-%Y %H:%M:%S')
        level = logging.DEBUG if self.settings.debug else logging.INFO
        self.logger = logging.Logger('bot', level=level)

        file_handler = logging.FileHandler('log.txt')
        file_handler.setLevel(level=level)
        file_handler.setFormatter(formatter)
        self.logger_file = file_handler

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=level)
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    async def init_longpoll(self, update=0):
        res = None
        retries = 10
        for _ in range(retries):
            res = self.api.method('messages.getLongPollServer', values={'group_id': 168105642, 'lp_version': 3})
            if res:
                break
            time.sleep(0.5)

        if not res:
            self.logger.critical('Unable to connect to VK long lopping server!')
            exit()
        ts = 0
        key = ''

        if update == 0:
            self.longpoll_server = "https://" + res['server']
            key = res['key']
            ts = res['ts']
        elif update == 3:
            key = res['key']
            ts = res['ts']
        elif update == 2:
            key = res['key']

        if 'ts' in self.longpoll_values:
            ts = self.longpoll_values['ts']
        if 'key' in self.longpoll_values:
            key = self.longpoll_values['key']

        self.longpoll_values = {
            'act': 'a_check',
            'group_id': 168105642,
            'key': key,
            'ts': ts,
            'wait': 20,
            'mode': 10,
            'version': 3
        }

    async def process_longpoll_event(self, event):
        if not event:
            return
        event_id = event[0]
        self.logger.info(event_id)

    async def longpoll_processor(self):
        await self.init_longpoll()

        session = aiohttp.ClientSession(loop=self.loop)
        while True:
            try:
                self.longpoll_request = session.get(self.longpoll_server, params=self.longpoll_values)
                resp = await self.longpoll_request
            except aiohttp.ClientOSError:
                session = aiohttp.ClientSession(loop=self.loop)
            except(asyncio.TimeoutError, aiohttp.ServerDisconnectedError):
                self.logger.warning('Long polling server doesn\'t respond. Changing server')
                await self.init_longpoll()
                continue

            print(resp)

            try:
                events = json.loads(await resp.text())
            except ValueError:
                continue

            print(events)

            failed = events.get('failed')
            if failed:
                err = int(failed)
                if err == 1:
                    self.longpoll_values['ts'] = events['ts']
                elif err in (2, 3):
                    await self.init_longpoll(err)
                continue
            self.longpoll_values['ts'] = events['ts']

            for event in events['updates']:
                await self.process_longpoll_event(event)

    def longpoll_run(self):
        self.main_task = Task(self.longpoll_processor())

        self.logger.info('Started to process messages')

        try:
            self.loop.run_until_complete(self.main_task)
        except(KeyboardInterrupt, SystemExit):
            self.stop()
            self.logger.info('Stopped to process messages')
        except asyncio.CancelledError:
            pass

    def stop(self):
        self.logger.removeHandler(self.logger_file)
        self.logger_file.close()


if __name__ == '__main__':
    bot = Bot(Settings)
