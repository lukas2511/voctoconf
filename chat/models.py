from django.db import models
import channels.layers
from asgiref.sync import async_to_sync


class Message(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=30)
    sender = models.CharField(max_length=30)
    content = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        send = self._state.adding
        models.Model.save(self, *args, **kwargs)
        if send:
            channel_layer = channels.layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)('chat_%s' % self.room, {'message': self.chatmsg(), 'type': 'chat_message'})

    def chatmsg(self):
        return "%s <%s> %s" % (self.date.strftime("%H:%M:%S"), self.sender, self.content)
