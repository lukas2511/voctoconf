from django.core.management.base import BaseCommand, CommandError
from bbb.models import Room, RoomStats
import requests
import json
import dateutil.parser
import traceback

class Command(BaseCommand):
    help = 'Update room statistics'

    def handle(self, *args, **options):
        for room in Room.objects.all():
            try:
                meetinginfo = room.api_meetinginfo()
                stats = RoomStats()
                stats.room = room
                stats.running = (meetinginfo['running'] == "true")

                if stats.running:
                    stats.recording = (meetinginfo['recording'] == "true")
                    stats.creation_date = dateutil.parser.parse(meetinginfo['createDate'])
                    stats.participants = int(meetinginfo['participantCount'])
                    stats.moderators = int(meetinginfo['moderatorCount'])
                    stats.videocount = int(meetinginfo['videoCount'])
                    stats.listeners = int(meetinginfo['listenerCount'])

                    if isinstance(meetinginfo['attendees']['attendee'], list):
                        attendees = meetinginfo['attendees']['attendee']
                    else:
                        attendees = [meetinginfo['attendees']['attendee']]
                    presenters = [a for a in attendees if a['isPresenter'] == 'true']
                    if presenters:
                        stats.presenter = presenters[0]['fullName']

                stats.save()
            except:
                print("Failed refreshing stats for %s" % room.id)
                traceback.print_exc()
