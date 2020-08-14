from django.core.management.base import BaseCommand, CommandError
from chat.models import Message
import requests
import json
import dateutil.parser
import traceback

class Command(BaseCommand):
    help = 'Send chat message'

    def add_arguments(self, parser):
        parser.add_argument('room', type=str)
        parser.add_argument('from', type=str)
        parser.add_argument('text', type=str)

    def handle(self, *args, **options):
        if options['room'] and options['from'] and options['text']:
            msg = Message()
            msg.room = options['room']
            msg.sender = options['from']
            msg.content = options['text']
            msg.save()

