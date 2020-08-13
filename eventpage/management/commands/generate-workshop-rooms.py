from django.core.management.base import BaseCommand, CommandError
from eventpage.models import Event
import bbb.models

import random
import requests
import json
import dateutil.parser

class Command(BaseCommand):
    help = 'Generate/Update BBB rooms for workshops'

    def handle(self, *args, **options):
        for event in Event.objects.filter(evtype="workshop"):
            new_room = False
            if not event.bbb:
                new_room = True
                event.bbb = bbb.models.Room()
            event.bbb.name = "Workshop: %s" % event.title
            event.bbb.server = random.choice(bbb.models.Server.objects.filter(for_workshops=True))
            event.bbb.record = False
            event.bbb.start_as_guest = True
            if new_room: event.bbb.save()
            event.save()

            for person in event.persons.all():
                if person.user and person.user not in event.bbb.moderators:
                    event.bbb.moderaors.add(person)
            event.bbb.save()

