import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, Connection, Ban
from .templatetags.is_chat_moderator import is_chat_moderator
import channels.layers

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
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        Connection.objects.filter(room=self.room_name, user=self.user_name).delete()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        type = text_data_json['type']
        if not type:
            return

        if type == 'chat_message' or type == 'whisper_message':
            message = Message()

            content = text_data_json['content']
            if not content or content.isspace():
                self.invalid_message()
                return
            
            message.sender = self.user_name
            if not message.sender:
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
            elif type == 'ban' or type == 'pardon':
                receiver = text_data_json['receiver']
                if not receiver or receiver.isspace():
                    self.invalid_message()
                    return
                if type == 'ban':
                    if Ban.objects.filter(user=receiver).count() == 0:
                        Ban.objects.get_or_create(user=receiver, reason=text_data_json['content'])
                        self.system_reply('Successfully banned "%s".' % receiver)
                    else:
                        self.system_reply('Couldn\'t ban "%s" because they are already banned.' % receiver)
                elif type == 'pardon':
                    if Ban.objects.filter(user=receiver).count() == 0:
                        self.system_reply('Couldn\'t pardon "%s" because they are not banned.' % receiver)
                    else:
                        Ban.objects.filter(user=receiver).delete()
                        self.system_reply('Successfully pardoned "%s".' % receiver)

        else:
            self.invalid_message()
    
    def send_message(self, message: Message, silent: bool = False):
        if message._state.adding:
            channel_layer = channels.layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)('chat_%s' % self.room_name,
                {
                    'type': Message.name_for_messagetype(message.type),
                    'message': message.chatmsg(),
                    'silent': silent
                })
    
    def invalid_message(self):
        self.system_reply("Invalid message.")
    
    def system_reply(self, content):
        message = Message()
        message.type = 'SYS'
        message.room = self.room_name
        message.receiver = self.user_name
        message.content = content
        self.send_message(message)
    
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
