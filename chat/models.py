from django.db import models
import channels.layers
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


messagetypes = (
    ('SYS', _('system_message')),
    ('MSG', _('chat_message')),
    ('WPR', _('whisper_message')),
)

class Message(models.Model):

    type = models.CharField(max_length=3, choices=messagetypes, default='MSG')
    date = models.DateTimeField(auto_now_add=True)
    # @TODO Fix magix number for chat room name length
    room = models.CharField(max_length=30)
    # @TODO Fix magix number for maximum username length
    sender = models.CharField(max_length=30)
    content = models.CharField(max_length=200)
    # @TODO Fix magix number for maximum username length
    receiver = models.CharField(max_length=30, null=True)

    def save(self, *args, **kwargs):
        models.Model.save(self, *args, **kwargs)
        
    def chatmsg(self):
        return {'date': timezone.localtime(self.date).strftime('%H:%M:%S'),
                'sender': self.sender,
                'content': self.content,
                'receiver': self.receiver}
    
    @staticmethod
    def name_for_messagetype(messagetype: str):
        return str(next(obj for obj in messagetypes if obj[0]==messagetype)[1])

class Bans(models.Model):
    # @TODO Fix magix number for maximum username length
    user = models.CharField(max_length=30)

class Connection(models.Model):
    # @TODO Fix magix number for chat room name length
    room = models.CharField(max_length=30)
    # @TODO Fix magix number for maximum username length
    user = models.CharField(max_length=30)