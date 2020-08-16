import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        type = text_data_json['type']
        message = text_data_json['message']

        if not message or not type or message.isspace():
            return
        
        msg = Message()
        msg.sender = self.get_name()
        if not msg.sender:
            return # wat?
        
        msg.content = message[:200]
        msg.room = self.room_name

        if type == "chat_message":
            msg.type = "MSG"
            
            msg.send()
            msg.save()

        elif type == "whisper_message":
            msg.type = "WPR"
            msg.receiver = text_data_json['target']
            if not msg.receiver:
                return
            msg.send()
    
    def get_name(self):
        if self.scope['user'].is_authenticated:
            return self.scope['user'].username
        elif 'name' in self.scope['session']:
            return "guest-%s" % self.scope['session']['name']
        else:
            return 

    # Receive message from room group
    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message']
        }))
    
    # Receive message from room group
    def whisper_message(self, event):
        message = event["message"]
        name = self.get_name()
        if name != message['receiver'] and name != message['sender']:
            return
        
        self.send(text_data=json.dumps({
            'type': event['type'],
            'sent': name != message['receiver'],
            'message': event['message']
        }))
    
    # Receive message from room group
    def system_message(self, event):
        message = event["message"]

        if self.scope['user'].username != message['receiver']:
            return
        
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message']
        }))
