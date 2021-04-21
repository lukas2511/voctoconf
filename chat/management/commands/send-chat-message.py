from chat.consumers import ChatConsumer
from chat.models import Message
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send chat message'

    def add_arguments(self, parser):
        parser.add_argument('-r','--room','--roomname',type=str)
        parser.add_argument('-f','--from', type=str)
        parser.add_argument('-t','--to', type=str)
        parser.add_argument('-T','--type', type=str, default='chat_message')
        parser.add_argument('text', type=str)

    def handle(self, *args, **options):
        if options['room'] and options['from'] and options['text']:
            msg = Message(room_name=options['room'],sender=options['from'],recipient=options['to'],content=options['text'])
            ChatConsumer.send_message(msg)
            msg.save()

