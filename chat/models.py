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
    
    def send(self):
        if self._state.adding:
            channel_layer = channels.layers.get_channel_layer()
            if(self.type=="WPR"):
                async_to_sync(channel_layer.group_send)('chat_%s' % self.room,
                    {
                        'type': str(next(obj for obj in messagetypes if obj[0]==self.type)[1]),
                        'message': self.chatmsg()
                    })
                if Connection.objects.filter(room=self.room, user=self.receiver).count() == 0:
                    error_message = Message()
                    error_message.type = "SYS"
                    error_message.room = self.room
                    error_message.receiver = self.sender
                    error_message.content = "Couldn't find user \"%s\" / Der Nutzer \"%s\" konnte nicht gefunden werden" % (self.receiver, self.receiver)
                    error_message.send()
            else:
                async_to_sync(channel_layer.group_send)('chat_%s' % self.room,
                    {
                        'type': str(next(obj for obj in messagetypes if obj[0]==self.type)[1]),
                        'message': self.chatmsg()
                    })
        
    def chatmsg(self):
        return {'date': timezone.localtime(self.date).strftime('%H:%M:%S'),
                'sender': self.sender,
                'content': self.content,
                'receiver': self.receiver}

class Bans(models.Model):
    # @TODO Fix magix number for maximum username length
    user = models.CharField(max_length=30)

class Connection(models.Model):
    # @TODO Fix magix number for chat room name length
    room = models.CharField(max_length=30)
    # @TODO Fix magix number for maximum username length
    user = models.CharField(max_length=30)