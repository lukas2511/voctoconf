import datetime
import re

import bbb.models
import partners.models
from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import utc
from django_tuieditor.widgets import StaticMarkdownViewerWidget
from django.db.models import Q

from .models import Announcement, Event, Person
from .models import Room as EventRoom


def event_overview(request):
    context = {}
    context['event_rooms'] = EventRoom.objects.filter(hide=False).filter(Q(stream__isnull=False) | Q(stream__isnull=False)).order_by('order')
    context['partners'] = partners.models.Partner.objects.filter(hide=False,is_project=False).order_by("order")
    context['projects'] = partners.models.Partner.objects.filter(hide=False,is_project=True).order_by("order")
    context['announcements_widget'] = StaticMarkdownViewerWidget()
    context['announcements'] = Announcement.objects.filter(hide=False).order_by('-id')
    context['hangouts'] = bbb.models.Room.objects.filter(hangout_room=True).order_by('hangout_order')

    try:
        context['poctisch'] = bbb.models.Room.objects.get(slug="poctischdummyforstats")
    except:
        context['poctisch'] = None

    context['workshops'] = []
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    another15minutes = datetime.timedelta(minutes=15)
    for workshop in Event.objects.filter(evtype="workshop", hide=False).order_by('start'):
        if (workshop.start - another15minutes) < now and (workshop.end + another15minutes) > now:
            context['workshops'].append(workshop)
            if workshop.start < now:
                context['workshops'][-1].nextup = True
        elif workshop.start > now and len(context['workshops']) < 2:
            context['workshops'].append(workshop)
            context['workshops'][-1].nextup = True

    return render(request, "event/overview.html", context)

def get_event(event_id: str):
    if event_id.isdigit():
        return get_object_or_404(Event, id=int(event_id))
    elif event_id:
        return get_object_or_404(Event, slug=event_id)
    else:
        raise Http404("No room found")

def event_view(request, eventid: str):
    event = get_event(eventid)
    return render(request, "event/event.html", {'event': event})

def person_view(request, pid):
    person = get_object_or_404(Person, id=pid)
    return render(request, "event/person.html", {'person': person})

def stream_view(request, roomid):
    if re.match(r'^[0-9]+$', roomid):
        room = get_object_or_404(EventRoom, id=int(roomid))
    else:
        room = get_object_or_404(EventRoom, slug=roomid)

    return render(request, "event/stream.html", {'room': room})
