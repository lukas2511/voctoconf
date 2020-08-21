from django.core.management.base import BaseCommand, CommandError
from bbb.models import Room, RoomStats, bbb_apicall
import requests
import json
import dateutil.parser
import traceback

class Command(BaseCommand):
    help = 'Update room statistics'

    def handle(self, *args, **options):
        room = Room.objects.get(slug="poctischdummyforstats")
        allmeetings = bbb_apicall(room.server.url, room.server.get_secret(), "getMeetings", {})
        if allmeetings['returncode'] != "SUCCESS":
            return

        if isinstance(allmeetings['meetings'], dict):
            meeting = allmeetings['meetings']['meeting']
            if meeting['meetingName'] != 'PoC Tisch':
                return

        else:
            search = [x for x in allmeetings['meetings'] if x['meeting']['meetingName'] == 'PoC Tisch']
            if not search:
                return
            meeting = search[0]

        stats = RoomStats()
        stats.room = room
        stats.running = True
        stats.participants = int(meeting['participantCount'])
        stats.save()
