from enum import Enum
import json
import logging
from typing import List, Optional, Union
from uuid import uuid4

import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.db import connections
from pydantic.main import BaseModel

from .models import Ban, Connections, Message, MessageTypes
from .templatetags.is_chat_moderator import is_chat_moderator
from django.apps import apps

log = logging.getLogger()

class ClientEventType(str, Enum):
    chat_message = 'chat_message',
    heartbeat = 'heartbeat',
    command = 'command'

class ClientCommand(BaseModel):
    command: str
    args: List[str] = []

class ClientEvent(BaseModel):
    type: ClientEventType
    payload: Union[ClientCommand, Message] = None

class ServerEventType(str, Enum):
    chat_message = 'chat_message',
    user_count = 'user_count'


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.config = apps.get_app_config('chat')
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
        event = ClientEvent(**json.loads(text_data))
        type = event.type

        if type == ClientEventType.chat_message:
            if not isinstance(event.payload, Message):
                return self.invalid_message()

            message: Message = event.payload
            if message.room_name != self.room_name:
                return self.invalid_message()
            
            silent = Ban.objects.filter(user_name=self.user_name).count() != 0

            if message.type == MessageTypes.whisper_message:
                if not message.recipient or message.recipient.isspace():
                    return self.system_reply('Missing target for command.')
                
                self.send_message(message, silent=silent)

                if Connections.has(self.room_name, message.recipient):
                    self.system_reply(f"Couldn't find user \"{message.recipient}\".")

            elif message.type == MessageTypes.chat_message:
                if message.recipient:
                    return self.invalid_message()
                
                self.send_message(message)
                message.save()

            elif message.type == MessageTypes.system_message:
                if not self.moderator:
                    return self.missing_perms()
                
                message.sender = '*system*'
                self.send_message(message)
                message.save()

        elif type == ClientEventType.heartbeat:
            Connections.add(room_name=self.room_name,
                            user_name=self.get_name())

        elif type == ClientEventType.command:
            if not isinstance(event.payload, ClientCommand):
                return self.invalid_message()
            
            self.handle_command(event.payload.command, event.payload.args)

        else:
            self.system_reply(f"Invalid event type: \"{type}\".")

    def handle_command(self, command: str, args: List[str]):
        if command == 'userlist':
            connections = Connections.get(room_name=self.room_name)
            usernames = ", ".join(c.decode('utf8') for c in connections)
            self.system_reply(f"Connected users ({len(connections)}): {usernames or '<none>'}")

        elif command == 'dice':
            self.system_reply('Rolled: 4')
            self.system_reply('// chosen by fair dice roll.')
            self.system_reply('// guaranteed to be random.')

        elif command == 'help':
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
                    '/baninfo <user_name> - display the reason why a user was banned')
                self.system_reply(
                    '/pardon <user_name> - revoke a user\'s ban so they can write in chat again')
                self.system_reply(
                    '/purge - cleare the whole backlog of saved messages')
        elif command == 'ban' or command == 'baninfo' or command == 'pardon':
            if not self.moderator:
                return self.missing_perms()
            if not len(args):
                return self.system_reply('Missing target for command.')
            target = args[0]
            if not target or target.isspace():
                return self.system_reply('Missing target for command.')
            
            if command == 'ban':
                if Ban.objects.filter(user=target).count() == 0:
                    Ban.objects.get_or_create(user=target, reason=' '.join(args[1:]))
                    self.system_reply(f"Successfully banned \"{target}\".")
                else:
                    self.system_reply(f"Couldn't ban \"{target}\" because they are already banned.")
            elif type == 'baninfo':
                queryset = Ban.objects.filter(user=target)
                if queryset.count() == 0:
                    self.system_reply(f"Couldn't get ban reason for \"{target}\" because they are not banned.")
                else:
                    self.system_reply(f"\"{target}\" was banned for the following reason: {queryset.first().reason}")
            elif type == 'pardon':
                if Ban.objects.filter(user=target).count() == 0:
                    self.system_reply(f"Couldn't pardon \"{target}\" because they are not banned.")
                else:
                    Ban.objects.filter(user=target).delete()
                    self.system_reply(f"Successfully pardoned \"{target}\".")
        elif type == 'purge':
            if not self.moderator:
                return self.missing_perms()
            
            Message.purge(self.room_name)
            self.system_reply('Cleared message backlog.')
        else:
            self.system_reply(f"Invalid command: \"{type}\".")

    @staticmethod
    def send_message(message: Message, silent: bool = False):
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"chat.{message.room_name}",
                                                {
                                                    'type': ServerEventType.chat_message,
                                                    'payload': message.dict(),
                                                    'silent': silent
                                                },)

    def system_reply(self, content):
        self.send(text_data=json.dumps({
            'type': ServerEventType.chat_message,
            'payload': Message(room_name = self.room_name, recipient = self.user_name, type = 'system_message', content = content).dict()
        }))
    
    def missing_perms(self):
        self.system_reply("I'm sorry, Dave. I'm afraid I can't do that.")
    
    def invalid_message(self):
        self.system_reply("Invalid message.")
    
    def update_user_count(self):
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(self.room_group_name,
                                                {
                                                    'type': ServerEventType.user_count,
                                                    'payload': Connections.count(self.room_name)
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
        message = event['payload']

        # If message is silent because the user is banned, only the sender can see the message they sent
        if event['silent'] and message['sender'] != self.user_name:
            return
        
        # If a recipient is set only send the message to sender and recipient
        if message['recipient'] and self.user_name != message['recipient'] and self.user_name != message['sender']:
            return

        self.send(text_data=json.dumps({
            'type': event['type'],
            'payload': event['payload']
        }))

    def user_count(self, event):
        self.send(text_data=json.dumps({
            'type': event['type'],
            'payload': event['payload']
        }))
