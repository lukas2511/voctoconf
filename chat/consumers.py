import json
import logging
from uuid import uuid4

import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Ban, Connections, Message
from .templatetags.is_chat_moderator import is_chat_moderator

log = logging.getLogger()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat.{self.room_name}"
        self.user_name = self.get_name()
        self.moderator = is_chat_moderator(self.scope['user'])

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        Connections.add(room_name=self.room_name, user_name=self.get_name())

        self.accept()
        self.update_user_count()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        self.update_user_count()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if not 'type' in text_data_json:
            self.invalid_message()
            return
        type = text_data_json['type']
        if not type:
            self.invalid_message()
            return

        # @TODO: fix magic values
        if type == 'chat_message' or type == 'whisper_message':
            content = text_data_json['content'][:200].strip()
            if not content:
                return
            
            message = Message(room_name=self.room_name, sender=self.user_name, type=type, content=content)
            
            if not message.validate or not message.sender:
                self.invalid_message()
                return

            silent = Ban.objects.filter(user_name=self.user_name).count() != 0

            if type == 'whisper_message':
                recipient = text_data_json['recipient']
                if not recipient or recipient.isspace():
                    self.invalid_message()
                    return
                message.recipient = recipient
                self.send_message(message, silent=silent)

                if Connections.has(self.room_name, recipient):
                    self.system_reply(f"Couldn't find user \"{recipient}\".")

            elif type == 'chat_message':
                self.send_message(message, silent=silent)
                if not silent:
                    message.save()

        elif type == 'heartbeat':
            Connections.add(room_name=self.room_name,
                            user_name=self.get_name())

        elif type == 'userlist':
            query_set = Connections.get(room_name=self.room_name)
            usernames = ", ".join(connection.decode('utf8')
                                  for connection in query_set)
            self.system_reply(
                f"Connected users ({len(query_set)}): {usernames or '<none>'}")

        elif type == 'dice':
            self.system_reply('Rolled: 4')
            self.system_reply('// chosen by fair dice roll.')
            self.system_reply('// guaranteed to be random.')

        elif type == 'help':
            self.system_reply('Available Commands:')
            self.system_reply('/w <user_name> <text> - private message')
            self.system_reply('/userlist - list of currently connected users')
            self.system_reply('/dice - roll a dice')
            self.system_reply('/help - this help')
            if self.moderator:
                self.system_reply('Moderator Commands:')
                self.system_reply(
                    '/system <text> - send a system message without sender')
                self.system_reply(
                    '/ban <user_name> [reason] - ban a user, their messages will no longer be visible to others')
                self.system_reply(
                    '/pardon <user_name> - revoke a user\'s ban so they can write in chat again')
                self.system_reply(
                    '/purge - cleare the whole backlog of saved messages')

        elif self.moderator:
            if type == 'system_message':
                content = text_data_json['content'][:200].strip()
                if not content:
                    return
                
                message = Message(room_name=self.room_name, sender=None, type=type, content=content)
                if not message.validate():
                    self.invalid_message()
                    return

                self.send_message(message)
                message.save()

            elif type == 'ban' or type == 'pardon':
                recipient = text_data_json['recipient']
                if not recipient or recipient.isspace():
                    self.invalid_message()
                    return
                if type == 'ban':
                    if Ban.objects.filter(user=recipient).count() == 0:
                        Ban.objects.get_or_create(
                            user=recipient, reason=text_data_json['content'])
                        self.system_reply(
                            'Successfully banned "%s".' % recipient)
                        self.system_reply(
                            'You may also want to delete their messages from the record using /purge <user_name>')
                    else:
                        self.system_reply(
                            'Couldn\'t ban "%s" because they are already banned.' % recipient)
                elif type == 'pardon':
                    if Ban.objects.filter(user=recipient).count() == 0:
                        self.system_reply(
                            'Couldn\'t pardon "%s" because they are not banned.' % recipient)
                    else:
                        Ban.objects.filter(user=recipient).delete()
                        self.system_reply(
                            'Successfully pardoned "%s".' % recipient)
            elif type == 'purge':
                Message.purge(self.room_name)
                self.system_reply('Cleared message backlog.')
            else:
                self.system_reply("Invalid command \"%s\"." % type)

        else:
            self.system_reply("Invalid command \"%s\"." % type)

    @staticmethod
    def send_message(message: Message, silent: bool = False):
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"chat.{message.room_name}",
                                                {
                                                    'type': 'chat_message',
                                                    'message': message.to_json(),
                                                    'silent': silent
                                                })

    def system_reply(self, content):
        self.send_message(Message(room_name = self.room_name, recipient = self.user_name, type = 'system_message', content = content))
    
    def invalid_message(self):
        self.system_reply("Invalid message.")
    
    def update_user_count(self):
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(self.room_group_name,
                                                {
                                                    'type': 'usercount',
                                                    'message': Connections.count(self.room_name)
                                                })

    def get_name(self):
        if self.scope['user'].is_authenticated:
            return self.scope['user'].username
        elif 'name' in self.scope['session']:
            return "guest-%s" % self.scope['session']['name']
        else:
            return

    ######
    # Outbound messages
    ######

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # If message is silent because the user is banned, only the sender can see the message they sent
        if event['silent'] and message['sender'] != self.user_name:
            return
        
        print(message)
        print(self.user_name)
        # If a recipient is set only send the message to sender and recipient
        if message['recipient'] and self.user_name != message['recipient'] and self.user_name != message['sender']:
            return

        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message']
        }))

    def usercount(self, event):
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event["message"]
        }))
