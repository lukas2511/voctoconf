import json
import math
import time
from datetime import datetime
from uuid import UUID, uuid4

import redis
from asgiref.sync import async_to_sync
from django.db import connections, models
from django.utils.translation import gettext_lazy as _
from marshmallow import Schema, fields, validate
from marshmallow.decorators import post_load

r = redis.Redis('localhost', 6379)
backlog_length = 100
connection_ttl = 15000


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
        # Automatically remove backlog when it's too long
        if backlog_length >= 0:
            r.ltrim(f"chat/{self.room_name}/messages", -backlog_length, -1)

    @staticmethod
    def getMessages(room_name: str, count: int = backlog_length):
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


class Connection():
    def add(room_name: str, user_name: str, connection_id: UUID = uuid4()):
        r.zadd(f"chat/{room_name}/connections",
               json.dumps({user_name, connection_id}, sort_keys=True))
        r.zremrangebyscore(
            f"chat/{room_name}/connections", -math.inf, time.time()-connection_ttl)
        return connection_id

    def remove(room_name: str, user_name: str, connection_id: UUID):
        r.zrem(f"chat/{room_name}/connections",
               json.dumps({user_name, connection_id}, sort_keys=True))

    def count(room_name: str):
        r.zcount(f"chat/{room_name}/connections",
                 time.time()-connection_ttl, math.inf)

    def get(room_name: str, user_name: str = None):
        r.zcount(f"chat/{room_name}/connections",
                 time.time()-connection_ttl, math.inf)
