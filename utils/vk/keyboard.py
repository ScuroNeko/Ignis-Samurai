import json
from enum import Enum

from utils.vk.utils import EnumEncoder


class VkKeyboardColor(Enum):
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    NEGATIVE = 'negative'
    POSITIVE = 'positive'


class VkKeyboard:
    def __init__(self, one_time=False, inline=False):
        self.inline = inline
        self.lines = [[]]

        self.keyboard = {
            'one_time': one_time,
            'inline': self.inline,
            'buttons': self.lines
        }

    def add_text_button(self, text, color=VkKeyboardColor.PRIMARY, payload=None):
        current_line = self.lines[-1]
        if len(current_line) == 5:
            raise TypeError('max elements in line: 5')

        action = {
            'type': 'text',
            'label': text
        }
        if payload:
            if type(payload) == str:
                action.update({'payload': payload})
            else:
                action.update({'payload': json.dumps(payload)})
        button = {
            'color': color,
            'action': action
        }
        current_line.append(button)

    def add_link_button(self, text, link, payload=None):
        current_line = self.lines[-1]
        if len(current_line) == 5:
            raise TypeError('max elements in line: 5')

        action = {
            'type': 'open_link',
            'link': link,
            'label': text
        }
        if payload:
            if type(payload) == str:
                action.update({'payload': payload})
            else:
                action.update({'payload': json.dumps(payload)})
        button = {
            'action': action
        }
        current_line.append(button)

    def add_location_button(self, payload=None):
        current_line = self.lines[-1]
        if len(current_line) == 5:
            raise TypeError('max elements in line: 5')

        action = {
            'type': 'location'
        }

        if payload:
            if type(payload) == str:
                action.update({'payload': payload})
            else:
                action.update({'payload': json.dumps(payload)})

        button = {
            'action': action
        }
        current_line.append(button)

    def add_vk_pay_button(self, hash):
        current_line = self.lines[-1]
        if len(current_line) == 5:
            raise TypeError('max elements in line: 5')

        action = {
            'type': 'vkpay',
            'hash': hash
        }
        button = {
            'action': action
        }
        current_line.append(button)

    def add_vk_apps_button(self, label, app_id, owner_id=None, hash=None, payload=None):
        current_line = self.lines[-1]
        if len(current_line) == 5:
            raise TypeError('max elements in line: 5')

        action = {
            'type': 'open_app',
            'label': label,
            'app_id': app_id
        }
        if owner_id:
            action.update({'owner_id': owner_id})
        if hash:
            action.update({'hash': hash})
        if payload:
            if type(payload) == str:
                action.update({'payload': payload})
            else:
                action.update({'payload': json.dumps(payload)})

        button = {
            'action': action
        }
        current_line.append(button)

    def add_callback_button(self, label, color=VkKeyboardColor.PRIMARY, payload=None):
        current_line = self.lines[-1]
        if len(current_line) == 5:
            raise TypeError('max elements in line: 5')

        action = {
            'type': 'callback',
            'label': label
        }

        if payload:
            if type(payload) == str:
                action.update({'payload': payload})
            else:
                action.update({'payload': json.dumps(payload)})

        button = {
            'action': action,
            'color': color
        }
        current_line.append(button)

    def add_line(self):
        if len(self.lines) == 10:
            if self.inline:
                raise TypeError('max lines: 6')
            else:
                raise TypeError('max lines: 10')
        self.lines.append([])

    def get_keyboard(self):
        keyboard = self.keyboard.copy()
        keyboard.update({'buttons': self.lines})
        return json.dumps(keyboard, cls=EnumEncoder)

    @classmethod
    def get_empty_keyboard(cls):
        keyboard = {
            'one_time': True,
            'buttons': []
        }
        return json.dumps(keyboard, cls=EnumEncoder)
