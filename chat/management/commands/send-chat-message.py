from chat.consumers import ChatConsumer
import json
from chat.models import Message
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send chat message'

    def add_arguments(self, parser):
        parser.add_argument('room', type=str)
        parser.add_argument('from', type=str)
        parser.add_argument('text', type=str)

    def handle(self, *args, **options):
        if options['room'] and options['from'] and options['text']:
            msg = Message(room_name=options['room'],sender=options['from'],content=options['text'])
            ChatConsumer.send_message(msg)
            msg.save()

