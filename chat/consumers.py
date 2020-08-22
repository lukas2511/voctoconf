import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, Connection, Ban
from .templatetags.is_chat_moderator import is_chat_moderator
import channels.layers
from datetime import datetime, timedelta

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user_name = self.get_name()
        self.moderator = is_chat_moderator(self.scope['user'])

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        Connection.objects.get_or_create(room=self.room_name, user=self.get_name())
        self.update_user_count()
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        Connection.objects.filter(room=self.room_name, user=self.user_name).delete()
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

        if type == 'chat_message' or type == 'whisper_message':
            message = Message()

            content = text_data_json['content']
            if not content or content.isspace():
                return
            
            message.sender = self.user_name
            if not message.sender:
                self.invalid_message()
                return # wat?
            
            message.content = content[:200]
            message.room = self.room_name

            silent = Ban.objects.filter(user=self.user_name).count() != 0

            if type == 'whisper_message':
                # @TODO: fix magic values
                message.type = "WPR"
                receiver = text_data_json['receiver']
                if not receiver or receiver.isspace():
                    self.invalid_message()
                    return
                message.receiver = receiver
                self.send_message(message, silent=silent)

                if Connection.objects.filter(room=self.room_name, user=receiver).count() == 0:
                    self.system_reply("Couldn't find user \"%s\"." % receiver)
            elif type == 'chat_message':
                message.type = "MSG"
                self.send_message(message, silent=silent)
                if not silent:
                    message.save()

        elif type == 'userlist':
            usernames = ", ".join(connection.user for connection in Connection.objects.filter(room=self.room_name))
            self.system_reply('Connected users: %s' % (usernames or '<none>'))
        
        elif type == 'purgeme':
            Message.objects.filter(room=self.room_name, sender=self.user_name).delete()
            self.system_reply('Deleted all saved messages sent by you.')

        elif type == 'help':
            self.system_reply('Available Commands:')
            self.system_reply('/w <user_name> <text> - private message')
            self.system_reply('/userlist - list of currently connected users')
            self.system_reply('/purgeme - delete all of the saved messages sent by you')
            self.system_reply('/help - this help')
            if self.moderator:
                self.system_reply('Moderator Commands:')
                self.system_reply('/system <text> - send a system message without sender')
                self.system_reply('/ban <user_name> [reason] - ban a user, their messages will no longe be visible to others')
                self.system_reply('/pardon <user_name> - revoke a user\'s ban so they can write in chat again')
                self.system_reply('/purge <user_name> - delete all of the saved messages sent by a user')
                self.system_reply('/decay - delete all saved chat messages older than 2 hours')

        elif self.moderator:
            if type == 'system_message':
                message = Message()
                content = text_data_json['content']
                if not content or content.isspace():
                    self.invalid_message()
                    return
                message.type = "SYS"
                message.content = content[:200]
                message.room = self.room_name
                self.send_message(message)
                message.save()
            elif type == 'ban' or type == 'pardon' or type == 'purge':
                receiver = text_data_json['receiver']
                if not receiver or receiver.isspace():
                    self.invalid_message()
                    return
                if type == 'ban':
                    if Ban.objects.filter(user=receiver).count() == 0:
                        Ban.objects.get_or_create(user=receiver, reason=text_data_json['content'])
                        self.system_reply('Successfully banned "%s".' % receiver)
                        self.system_reply('You may also want to delete their messages from the record using /purge <user_name>')
                    else:
                        self.system_reply('Couldn\'t ban "%s" because they are already banned.' % receiver)
                elif type == 'pardon':
                    if Ban.objects.filter(user=receiver).count() == 0:
                        self.system_reply('Couldn\'t pardon "%s" because they are not banned.' % receiver)
                    else:
                        Ban.objects.filter(user=receiver).delete()
                        self.system_reply('Successfully pardoned "%s".' % receiver)
                elif type == 'purge':
                    Message.objects.filter(sender=receiver).delete()
                    self.system_reply('Deleted all saved messages sent by user "%s".' % receiver)
            elif type == 'decay':
                Message.objects.filter(room=self.room_name, date__lt=datetime.now() - timedelta(hours=2)).delete()
                self.system_reply('Cleared all saved messages older than 2 hours.')
            elif type == 'clearall':
                Message.objects.all(room=self.room_name).delete()
                self.system_reply('Cleared all saved messages.')
            else:
                self.system_reply("Invalid command \"%s\"." % type)

        else:
            self.system_reply("Invalid command \"%s\"." % type)
    
    def send_message(self, message: Message, silent: bool = False):
        if message._state.adding:
            channel_layer = channels.layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)('chat_%s' % self.room_name,
                {
                    'type': Message.name_for_messagetype(message.type),
                    'message': message.chatmsg(),
                    'silent': silent
                })
    
    def update_user_count(self):
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)('chat_%s' % self.room_name,
            {
                'type': 'usercount',
                'message': Connection.objects.filter(room=self.room_name).count()
            })
    
    def invalid_message(self):
        self.system_reply("Invalid message.")
    
    def system_reply(self, content):
        message = Message()
        message.type = 'SYS'
        message.room = self.room_name
        message.receiver = self.user_name
        message.content = content
        self.system_message({
                    'type': Message.name_for_messagetype(message.type),
                    'message': message.chatmsg()
                })
    
    def get_name(self):
        if self.scope['user'].is_authenticated:
            return self.scope['user'].username
        elif 'name' in self.scope['session']:
            return "guest-%s" % self.scope['session']['name']
        else:
            return 


    # Receive message from room group
    def chat_message(self, event):
        # If message is silent because the user is banned, only the sender can see the message they sent
        if event['silent']:
            if event["message"]['sender'] != self.user_name:
                return
        
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message']
        }))
    
    # Receive message from room group
    def whisper_message(self, event):
        message = event["message"]

        # If message is silent because the user is banned, only the sender can see the message they sent
        if event['silent']:
            if message['sender'] != self.user_name:
                return
        
        if self.user_name != message['receiver'] and self.user_name != message['sender']:
            return
        
        self.send(text_data=json.dumps({
            'type': event['type'],
            'sent': self.user_name != message['receiver'],
            'message': event['message']
        }))
    
    # Receive message from room group
    def system_message(self, event):
        message = event["message"]
        if message['receiver'] and self.user_name != message['receiver']:
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
