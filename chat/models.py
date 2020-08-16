from django.db import models
import channels.layers
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class MessageType(models.TextChoices):
    SYSTEM = 'SYS', _('system_message')
    MESSAGE = 'MSG', _('chat_message')
    WHISPER = 'WPR', _('whisper_message')

class Message(models.Model):

    type = models.CharField(max_length=3, choices=MessageType.choices, default=MessageType.MESSAGE)
    date = models.DateTimeField(auto_now_add=True)
    # @TODO Fix magix number for maximum username length
    room = models.CharField(max_length=30)
    sender = models.CharField(max_length=30)
    content = models.CharField(max_length=200)
    # @TODO Fix magix number for maximum username length
    receiver = models.CharField(max_length=30, null=True)

    def save(self, *args, **kwargs):
        models.Model.save(self, *args, **kwargs)
    
    def send(self):
        if self._state.adding:
            channel_layer = channels.layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)('chat_%s' % self.room, 
                {
                    'type': str(MessageType(self.type).label),
                    'message': self.chatmsg()
                })
        
    def chatmsg(self):
        return {'date': timezone.localtime(self.date).strftime('%H:%M:%S'),
                'sender': self.sender,
                'content': self.content,
                'receiver': self.receiver}
