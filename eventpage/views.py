from django.shortcuts import render
from authstuff.names import name_required
from django.http import HttpResponse
from .models import Room as EventRoom, Event
import partners.models

def event_view(request):
    context = {}
    context['event_rooms'] = EventRoom.objects.filter(hide=False).order_by('order')
    context['workshops'] = Event.objects.filter(evtype="workshop", hide=False).order_by('start')
    context['partners'] = partners.models.Partner.objects.all().order_by("order")
    return render(request, "event/event.html", context)
