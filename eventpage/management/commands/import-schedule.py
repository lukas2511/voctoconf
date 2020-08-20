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
        parser.add_argument('--persons', required=True, type=str)

    def parse_person(self, person):
        if Person.objects.filter(id=person['id']).exists():
            obj = Person.objects.get(id=person['id'])
            if obj.custom:
                return obj.id
        else:
            obj = Person()
            obj.id = person['id']

        if not obj.name_modified:
            obj.name = person['public_name']

        if not obj.image_modified:
            obj.image = person['image']
            if obj.image:
                obj.image = "https://programm.froscon.de/2020" + obj.image.replace("/original/", "/large/")

        if not obj.abstract_modified:
            obj.abstract = person['abstract']

        if not obj.description_modified:
            obj.description = person['description']

        obj.save()
        return obj.id

    def parse_event(self, event):
        if Event.objects.filter(id=event['id']).exists():
            obj = Event.objects.get(id=event['id'])
            if obj.custom:
                return obj.id
        else:
            obj = Event()
            obj.id = event['id']

        if not obj.start_modified:
            obj.start = dateutil.parser.parse(event['date'])

        if not obj.end_modified:
            hoursstr, minutesstr = event['duration'].split(':')
            obj.end = obj.start + datetime.timedelta(hours=int(hoursstr), minutes=int(minutesstr))

        if not obj.abstract_modified:
            obj.abstract = event['abstract']

        if not obj.description_modified:
            obj.description = event['description']

        if not obj.logo_modified:
            obj.logo = event['logo']
            if obj.logo:
                obj.logo = "https://programm.froscon.de/2020" + obj.logo

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
        return obj.id

    def handle(self, *args, **options):
        if options["schedule"]:
            actual_events = []
            schedule = json.loads(requests.get(options["schedule"]).text)
            for day in schedule["schedule"]["conference"]["days"]:
                for _, events in day["rooms"].items():
                    for event in events:
                        actual_events.append(self.parse_event(event))

            for event in Event.objects.all():
                if event.id not in actual_events and not event.custom:
                    print("Event %d not found in schedule: %s" % (event.id, event.title))

        if options["persons"]:
            actual_persons = []
            persons = json.loads(requests.get(options["persons"]).text)
            for person in persons["schedule_speakers"]["speakers"]:
                actual_persons.append(self.parse_person(person))

            for person in Person.objects.all():
                if person.id not in actual_persons and not person.custom:
                    print("Person %d not found in schedule: %s" % (person.id, person.name))

