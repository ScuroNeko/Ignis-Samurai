from handler.vk.vk_command_plugin import VKCommandPlugin


class TestPlugin(VKCommandPlugin):
    def __init__(self, prefixes):
        """
        Плагин, который будет работать только в ВК
        :param prefixes:
        """
        self.commands = ['test']
        super().__init__(self.commands, prefixes)

    def msg_process(self, msg):
        return msg.answer('TEST')

    def event_check(self, event):
        if event.type == 'chat_title_update':
            return True

    def event_process(self, event):
        user = self.api.users.get(user_ids=event.user_id)[0]
        return self.api.messages.send(peer_id=event.peer_id,
                                      message=f'{user["first_name"]} {user["last_name"]} '
                                      f'изменил название чата на {event.text}')
