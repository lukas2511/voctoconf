from django.apps import AppConfig
from logging import getLogger
from redis import Redis

log = getLogger("chat")

class ChatConfig(AppConfig):
    name = 'chat'
    verbose_name = 'Chat'
    redis_host: str = None
    redis_port: int = 6379
    redis_instance: Redis  = None
    backlog_length = 100
    max_message_length = 200
    connection_ttl = 5

    def ready(self):
        if not self.redis_instance:
            if not self.redis_host:
                log.warn('Redis host was not set, defaulting to localhost')
            self.redis_instance = Redis(self.redis_host or 'localhost', self.redis_port)
        else:
            log.debug('Using supplied Redis instance')
    
    def get_redis(self) -> Redis:
        return self.redis_instance