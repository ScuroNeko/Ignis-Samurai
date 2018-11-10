# -*- coding: utf-8 -*-
import asyncio
import logging
from asyncio import Task

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.longpoll import VkLongPoll

from handler.handler import MessageHandler
from settings import Settings
from utils.data import Message, LongpollEvent


class Bot:
    def __init__(self, settings):
        self.settings = settings
        self.loop = asyncio.get_event_loop()
        # Logging
        self.logger = None
        self.logger_file = None

        # VK
        self.session = None
        self.api = None
        self.auth_method = ''

        self.init_logger()
        self.auth()
        self.handler = MessageHandler(self, self.api)
        self.listen_longpoll()

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

    def auth(self):
        self.auth_method = self.settings.auth[0]
        if self.auth_method == 'user':
            if len(self.settings.auth) == 2:  # Token auth
                token = self.settings.auth[1]
                self.session = vk_api.VkApi(token=token, api_version='5.87')
            elif len(self.settings.auth) == 3:  # Login + Password auth
                login, password = self.settings.auth[1], self.settings.auth[2]
                self.session = vk_api.VkApi(login, password,
                                            app_id=self.settings.app_id,
                                            scope=self.settings.scope)
            elif len(self.settings.auth) <= 1:
                self.logger.critical('Token or login/password not set!')
                exit()
            else:
                self.logger.critical('Unexpected auth error!')
                exit()

            try:
                self.session.auth(token_only=True)
            except vk_api.AuthError as error_msg:
                self.logger.critical(error_msg)
                exit()
            self.api = self.session.get_api()
            user = self.api.users.get()
            self.logger.info('Login as {} {} (https://vk.com/id{})'.
                             format(user[0]['first_name'], user[0]['last_name'], user[0]['id']))
        elif self.auth_method == 'group':
            if len(self.settings.auth) <= 1:
                self.logger.critical('Token not set!')
                exit()
            else:
                self.session = vk_api.VkApi(token=self.settings.auth[1], api_version='5.87')
                try:
                    self.api = self.session.get_api()
                    self.api.messages.getLongPollServer()
                except vk_api.ApiError:
                    self.logger.critical('Wrong token!')
                    exit()
            group = self.api.groups.getById()
            self.logger.info('Login as {} (https://vk.com/{})'.
                             format(group[0]['name'],
                                    group[0]['screen_name'] if 'screen_name' in group[0] else f'public{group[0]["id"]}'))
        else:
            self.logger.critical('Unexpected auth error!')
            exit()

    def listen_longpoll(self):
        global longpoll
        if self.auth_method == 'group':
            longpoll = VkBotLongPoll(self.session, self.api.groups.getById()[0]['id'])
        elif self.auth_method == 'user':
            longpoll = VkLongPoll(self.session)
        else:
            self.logger.critical('Unexpected error!')
            exit()

        self.logger.info('Started to process messages')
        self.handler.initiate()
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and 'action' not in event.raw['object']:
                    try:
                        task = Task(self.process_message(event.raw['object']))
                        self.loop.run_until_complete(task)
                    except Exception as e:
                        self.logger.error(e)
                else:
                    try:
                        task = Task(self.process_event(event.raw))
                        self.loop.run_until_complete(task)
                    except Exception as e:
                        self.logger.error(e)
        except KeyboardInterrupt:
            self.stop()

    async def process_message(self, data):
        await asyncio.ensure_future(self.handler.process(Message(self.api, data)), loop=self.loop)

    async def process_event(self, event):
        await asyncio.ensure_future(self.handler.process_event(LongpollEvent(self.api, event)), loop=self.loop)

    def stop(self):
        self.logger.removeHandler(self.logger_file)
        self.logger_file.close()
        self.logger.info('Stopped to process messages')


if __name__ == '__main__':
    bot = Bot(Settings)
