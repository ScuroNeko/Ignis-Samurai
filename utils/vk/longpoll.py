from enum import Enum

from utils.vk.vk import VK


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class VKLongPoll:
    __slots__ = ('vk', 'api', 'server', 'key', 'ts', 'group_id')

    def __init__(self, vk: VK):
        self.vk = vk
        self.api = vk.get_api()
        self.group_id = 0

        self.server = ''
        self.key = ''
        self.ts = 0

    async def init_lp(self):
        if not self.group_id:
            group = (await self.api.groups.getById())[0]
            self.group_id = group['id']
        lp = await self.api.groups.getLongPollServer(group_id=self.group_id)

        self.server = lp['server']
        self.key = lp['key']
        self.ts = lp['ts']

    async def check(self):
        async with self.vk.session.get(f'{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait=25') as res:
            body = await res.json()
            if 'failed' in body:
                code = body['failed']
                if code == 1:
                    self.ts = body['ts']
                if code == 2 or code == 3:
                    await self.init_lp()
            else:
                self.ts = body['ts']
            for event in body['updates']:
                yield VkBotEvent(event)

    async def listen(self):
        while True:
            async for event in self.check():
                yield event


class VkBotEvent(object):
    __slots__ = (
        'raw',
        't', 'type',
        'obj', 'object',
        'client_info', 'message',
        'group_id'
    )

    def __init__(self, raw):
        self.raw = raw

        try:
            self.type = VkBotEventType(raw['type'])
        except ValueError:
            self.type = raw['type']

        self.t = self.type  # shortcut

        self.object = DotDict(raw['object'])
        try:
            self.message = DotDict(raw['object']['message'])
        except KeyError:
            self.message = None
        self.obj = self.object
        try:
            self.client_info = DotDict(raw['object']['client_info'])
        except KeyError:
            self.client_info = None

        self.group_id = raw['group_id']

    def __repr__(self):
        return '<{}({})>'.format(type(self), self.raw)


class VkBotEventType(Enum):
    MESSAGE_NEW = 'message_new'
    MESSAGE_REPLY = 'message_reply'
    MESSAGE_EDIT = 'message_edit'
    MESSAGE_EVENT = 'message_event'

    MESSAGE_TYPING_STATE = 'message_typing_state'

    MESSAGE_ALLOW = 'message_allow'

    MESSAGE_DENY = 'message_deny'

    PHOTO_NEW = 'photo_new'

    PHOTO_COMMENT_NEW = 'photo_comment_new'
    PHOTO_COMMENT_EDIT = 'photo_comment_edit'
    PHOTO_COMMENT_RESTORE = 'photo_comment_restore'

    PHOTO_COMMENT_DELETE = 'photo_comment_delete'

    AUDIO_NEW = 'audio_new'

    VIDEO_NEW = 'video_new'

    VIDEO_COMMENT_NEW = 'video_comment_new'
    VIDEO_COMMENT_EDIT = 'video_comment_edit'
    VIDEO_COMMENT_RESTORE = 'video_comment_restore'

    VIDEO_COMMENT_DELETE = 'video_comment_delete'

    WALL_POST_NEW = 'wall_post_new'
    WALL_REPOST = 'wall_repost'

    WALL_REPLY_NEW = 'wall_reply_new'
    WALL_REPLY_EDIT = 'wall_reply_edit'
    WALL_REPLY_RESTORE = 'wall_reply_restore'

    WALL_REPLY_DELETE = 'wall_reply_delete'

    BOARD_POST_NEW = 'board_post_new'
    BOARD_POST_EDIT = 'board_post_edit'
    BOARD_POST_RESTORE = 'board_post_restore'

    BOARD_POST_DELETE = 'board_post_delete'

    MARKET_COMMENT_NEW = 'market_comment_new'
    MARKET_COMMENT_EDIT = 'market_comment_edit'
    MARKET_COMMENT_RESTORE = 'market_comment_restore'

    MARKET_COMMENT_DELETE = 'market_comment_delete'

    GROUP_LEAVE = 'group_leave'
    GROUP_JOIN = 'group_join'

    USER_BLOCK = 'user_block'
    USER_UNBLOCK = 'user_unblock'

    POLL_VOTE_NEW = 'poll_vote_new'

    GROUP_OFFICERS_EDIT = 'group_officers_edit'
    GROUP_CHANGE_SETTINGS = 'group_change_settings'
    GROUP_CHANGE_PHOTO = 'group_change_photo'

    VKPAY_TRANSACTION = 'vkpay_transaction'

    APP_PAYLOAD = 'app_payload'

    DONUT_SUBSCRIPTION_CREATE = 'donut_subscription_create'
    DONUT_SUBSCRIPTION_PROLONGED = 'donut_subscription_prolonged'
    DONUT_SUBSCRIPTION_EXPIRED = 'donut_subscription_expired'
    DONUT_SUBSCRIPTION_CANCELLED = 'donut_subscription_cancelled'
    DONUT_SUBSCRIPTION_PRICE_CHANGED = 'donut_subscription_price_changed'
    DONUT_SUBSCRIPTION_WITHDRAW = 'donut_money_withdraw'
    DONUT_SUBSCRIPTION_WITHDRAW_ERROR = 'donut_money_withdraw_error'