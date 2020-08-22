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
            print("Adding new person %d" % obj.id)

        if not obj.name_modified:
            newname = person['public_name']
            if obj.name != newname:
                print("Person %d name changed: %s -> %s" % (obj.id, obj.name, newname))
                obj.name = newname

        if not obj.image_modified:
            newimage = person['image']
            if newimage:
                newimage = "https://programm.froscon.de/2020" + newimage.replace("/original/", "/large/")

            if obj.image != newimage:
                print("Person %d image changed: %s -> %s" % (obj.id, obj.image, newimage))
                obj.image = newimage

        if not obj.abstract_modified:
            newabstract = person['abstract']
            if obj.abstract != newabstract:
                print("Person %d abstract changed: %s -> %s" % (obj.id, obj.abstract, newabstract))
                obj.abstract = newabstract

        if not obj.description_modified:
            newdescription = person['description']
            if obj.description != newdescription:
                print("Person %d description changed: %s -> %s" % (obj.id, obj.description, newdescription))
                obj.description = newdescription

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
            print("Adding new event %d" % obj.id)

        if not obj.start_modified:
            newstart = dateutil.parser.parse(event['date'])
            if obj.start != newstart:
                print("Event %d start changed: %r -> %r" % (obj.id, obj.start, newstart))
                obj.start = newstart

        if not obj.end_modified:
            hoursstr, minutesstr = event['duration'].split(':')
            newend = obj.start + datetime.timedelta(hours=int(hoursstr), minutes=int(minutesstr))
            if obj.end != newend:
                print("Event %d end changed: %r -> %r" % (obj.id, obj.end, newend))
                obj.end = newend

        if not obj.abstract_modified:
            newabstract = event['abstract']
            if obj.abstract != newabstract:
                print("Event %d abstract changed: %s -> %s" % (obj.id, obj.abstract, newabstract))
                obj.abstract = newabstract

        if not obj.description_modified:
            newdescription = event['description']
            if obj.description != newdescription:
                print("Event %d description changed: %s -> %s" % (obj.id, obj.description, newdescription))
                obj.description = newdescription

        if not obj.logo_modified:
            newlogo = event['logo']
            if newlogo:
                newlogo = "https://programm.froscon.de/2020" + newlogo
            if obj.logo != newlogo:
                print("Event %d logo changed: %s -> %s" % (obj.id, obj.logo, newlogo))
                obj.logo = newlogo

        if not obj.title_modified:
            newtitle = event['title']
            if obj.title != newtitle:
                print("Event %d title changed: %s -> %s" % (obj.id, obj.title, newtitle))
                obj.title = newtitle

        if not obj.evtype_modified:
            newevtype = event['type'] if event['type'] else 'undefined'
            if obj.evtype != newevtype:
                print("Event %d type changed: %s -> %s" % (obj.id, obj.evtype, newevtype))
                obj.evtype = newevtype

        if not obj.room_modified:
            if Room.objects.filter(name=event["room"]).exists():
                room = Room.objects.get(name=event["room"])
            else:
                room = Room()
                room.name = event["room"]
                room.save()

            if room != obj.room:
                print("Event %d room changed: %s -> %s" % (obj.id, obj.room, room))
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

            if track != obj.track:
                print("Event %d track changed: %s -> %s" % (obj.id, obj.track, track))
                obj.track = track

        obj.save()

        if not obj.persons_modified:
            holding = []
            for person in event['persons']:
                if Person.objects.filter(id=person['id']).exists():
                    pobj = Person.objects.get(id=person['id'])
                    if pobj not in obj.persons.all():
                        obj.persons.add(pobj)
                    holding.append(pobj)
                else:
                    print("Person %d (%s) for event %d (%s) not found, please re-import persons table" % (person['id'], person['public_name'], obj.id, obj.title))

            for pobj in obj.persons.all():
                if pobj not in holding:
                    obj.persons.remove(pobj)

        obj.save()
        return obj.id

    def handle(self, *args, **options):
        if options["persons"]:
            actual_persons = []
            persons = json.loads(requests.get(options["persons"]).text)
            for person in persons["schedule_speakers"]["speakers"]:
                actual_persons.append(self.parse_person(person))

            for person in Person.objects.all():
                if person.id not in actual_persons and not person.custom:
                    print("Removing person %d (not found in schedule): %s" % (person.id, person.name))
                    person.delete()

        if options["schedule"]:
            actual_events = []
            schedule = json.loads(requests.get(options["schedule"]).text)
            for day in schedule["schedule"]["conference"]["days"]:
                for _, events in day["rooms"].items():
                    for event in events:
                        actual_events.append(self.parse_event(event))

            for event in Event.objects.all():
                if event.id not in actual_events and not event.custom:
                    print("Removing event %d (not found in schedule): %s" % (event.id, event.title))
                    event.delete()

