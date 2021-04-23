from __future__ import annotations

import math
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from re import L
from typing import Iterable, List, Literal, Optional, Union

import json
from django.apps import apps
from django.db import models
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, validator
from redis import Redis

from chat.apps import ChatConfig


def _config() -> ChatConfig:
    return apps.get_app_config('chat')

def _redis() -> Redis:
    return _config().get_redis()

class MessageTypes(str, Enum):
    system_message = 'system_message'
    chat_message = 'chat_message'
    whisper_message = 'whisper_message'


class Message(BaseModel):
    room_name: str
    content: str
    sender: str = None
    recipient: Optional[str] = None
    type: MessageTypes = 'chat_message'
    time: str = datetime.now().isoformat()

    @validator('content')
    def validate_content(cls, value: str):
        content = value[:_config().max_message_length].strip()
        if not content:
            raise ValueError('Empty content')
        return content
    
    @validator('time')
    def validate_time(cls, value: str):
        time = datetime.fromisoformat(value)
        return time.isoformat()

    def save(self):
        pipeline = _redis().pipeline()
        pipeline.rpush(f"chat:{self.room_name}:messages", self.json())
        # Automatically remove backlog when it's too long

        backlog_length = _config().backlog_length
        pipeline.ltrim(f"chat:{self.room_name}:messages", -backlog_length if backlog_length else 0, -1)
        pipeline.execute()

    @staticmethod
    def purge(room_name: str) -> None:
        _redis().delete(f"chat:{room_name}:messages")

    @staticmethod
    def get_message_json_strings(room_name: str, count: int = None) -> Iterable[str]:
        return _redis().lrange(f"chat:{room_name}:messages", -count if count else 0, -1)
    
    @staticmethod
    def get_message_jsons(room_name: str, count: int = None) -> Iterable[dict]:
        return (json.loads(m) for m in Message.get_message_json_strings(room_name, count))
    
    @staticmethod
    def get_messages(room_name: str, count: int = None) -> Iterable[Message]:
        return (Message(**m) for m in Message.get_message_jsons(room_name, count))


class Ban(models.Model):
    user_name = models.CharField(max_length=64)
    reason = models.TextField(null=True, blank=True)


class Connections:
    def add(room_name: str, user_name: str):
        pipeline = _redis().pipeline()
        pipeline.zremrangebyscore(
            f"chat:{room_name}:connections", -math.inf, time.time()-_config().connection_ttl)
        pipeline.zadd(f"chat:{room_name}:connections",
                      {
                          user_name: time.time()
                      })
        pipeline.execute()

    def count(room_name: str):
        return _redis().zcount(f"chat:{room_name}:connections",
                        time.time()-_config().connection_ttl, math.inf) or 0

    def get(room_name: str, user_name: str = None) -> List[str]:
        return _redis().zrangebyscore(f"chat:{room_name}:connections", time.time()-_config().connection_ttl, math.inf)

    def has(room_name: str, user_name: str) -> bool:
        return user_name in _redis().zrangebyscore(f"chat:{room_name}:connections", time.time()-_config().connection_ttl, math.inf)
