from django.core.management.base import BaseCommand, CommandError
from eventpage.models import Room, Event, Person, Track
import requests
import json
import dateutil.parser
import datetime

class Command(BaseCommand):
    help = 'Import JSON schedule'

    def add_arguments(self, parser):
        parser.add_argument('--schedule', required=True, type=str)

    def parse_event(self, event):
        if Event.objects.filter(id=event['id']).exists():
            obj = Event.objects.get(id=event['id'])
        else:
            obj = Event()
            obj.id = event['id']

        if not obj.start_modified:
            obj.start = dateutil.parser.parse(event['date'])

        if not obj.end_modified:
            hoursstr, minutesstr = event['duration'].split(':')
            obj.end = obj.start + datetime.timedelta(hours=int(hoursstr), minutes=int(minutesstr))

        if not obj.title_modified:
            obj.title = event['title']

        if not obj.evtype_modified:
            obj.evtype = event['type'] if event['type'] else 'undefined'

        if not obj.room_modified:
            if Room.objects.filter(name=event["room"]).exists():
                room = Room.objects.get(name=event["room"])
            else:
                room = Room()
                room.name = event["room"]
                room.save()

            obj.room = room

        if not obj.track_modified:
            if not event["track"]:
                event["track"] = "None"
            if Track.objects.filter(name=event["track"]).exists():
                track = Track.objects.get(name=event["track"])
            else:
                track = Track()
                track.name = event["track"]
                track.save()

            obj.track = track

        if not obj.persons_modified:
            holding = []
            for person in event['persons']:
                if Person.objects.filter(id=person['id']).exists():
                    pobj = Person.objects.get(id=person['id'])
                else:
                    pobj = Person()
                    pobj.id = person['id']

                if not pobj.name_modified:
                    pobj.name = person['public_name']
                    pobj.save()

                if pobj not in obj.persons.all():
                    obj.persons.add(pobj)

                holding.append(pobj)

            for pobj in obj.persons.all():
                if pobj not in holding:
                    obj.persons.remove(pobj)

        obj.save()

    def handle(self, *args, **options):
        schedule = json.loads(requests.get(options["schedule"]).text)

        for day in schedule["schedule"]["conference"]["days"]:
            for _, events in day["rooms"].items():
                for event in events:
                    self.parse_event(event)
