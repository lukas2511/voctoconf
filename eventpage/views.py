from django.shortcuts import render
from authstuff.names import name_required
from django.http import HttpResponse
from .models import Room as EventRoom, Event, Announcement
import partners.models
from django.utils.timezone import utc
import datetime

def event_view(request):
    context = {}
    context['event_rooms'] = EventRoom.objects.filter(hide=False).order_by('order')
    context['partners'] = partners.models.Partner.objects.all().order_by("order")
    context['announcements'] = Announcement.objects.filter(hide=False).order_by('-id')

    context['workshops'] = []
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    another15minutes = datetime.timedelta(minutes=15)
    for workshop in Event.objects.filter(evtype="workshop", hide=False).order_by('start'):
        if (workshop.start + another15minutes) > now and (workshop.end - another15minutes) < now:
            context['workshops'].append(workshop)
            if workshop.start < now:
                context['workshops'][-1].nextup = True
        elif workshop.start > now and len(context['workshops']) < 2:
            context['workshops'].append(workshop)
            context['workshops'][-1].nextup = True

    return render(request, "event/event.html", context)
