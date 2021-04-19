from typing import Literal, Union
from django.db import models
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from marshmallow.decorators import post_load
import redis
from marshmallow import Schema, fields, validate
from datetime import date, datetime

r = redis.Redis('localhost', 6379)


class Message:
    def __init__(self, time=datetime.now(), sender=None, content=None, receiver=None, room_name=None, type=None):
        self.time = time
        self.sender = sender
        self.content = content
        self.receiver = receiver
        self.room_name = room_name
        self.type = type

    def save(self):
        r.rpush(f"chat/{self.room_name}/messages",
                self.to_json_string().encode('utf8'))

    @staticmethod
    def getMessages(room_name, count):
        return (message_schema.loads(m.decode('utf8')) for m in r.lrange(f"chat/{room_name}/messages", -count, -1))

    def to_json(self) -> dict:
        return message_schema.dump(self)

    def to_json_string(self) -> str:
        return message_schema.dumps(self)


class MessageSchema(Schema):
    time = fields.DateTime()
    sender = fields.String()
    content = fields.String()
    receiver = fields.String(allow_none=True)
    room_name = fields.String()
    type = fields.String(
        required=True,
        validate=validate.OneOf(
            ['system_message', 'chat_message', 'whisper_message']
        ))

    @post_load
    def make_message(self, data, **kwargs):
        return Message(**data)
message_schema = MessageSchema()


class Ban(models.Model):
    # @TODO Fix magix number for maximum username length
    user = models.CharField(max_length=30)
    reason = models.CharField(max_length=200, null=True, blank=True)


class Connection(models.Model):
    # @TODO Fix magix number for chat room name length
    room = models.CharField(max_length=30)
    # @TODO Fix magix number for maximum username length
    user = models.CharField(max_length=30)
