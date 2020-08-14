from django.core.management.base import BaseCommand, CommandError
from bbb.models import Room, RoomStats
import requests
import json
import dateutil.parser
import traceback

class Command(BaseCommand):
    help = 'Close room'

    def add_arguments(self, parser):
        parser.add_argument('--id', required=True, type=str)

    def handle(self, *args, **options):
        room = Room.objects.get(id=options['id'])
        meetinginfo = room.api_meetinginfo()
        print(json.dumps(meetinginfo, indent=4))
