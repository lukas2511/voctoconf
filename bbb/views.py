from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from .models import Room
from authstuff.names import name_required
from django.http import HttpResponse
import json

@name_required
def roomview(request, roomid):
    room = get_object_or_404(Room, id=roomid)

    if request.GET.get("ended"):
        return render(request, "bbb/roomended.html")

    meeting = room.join(request, name=request.username)

    if meeting:
        if request.GET.get("noframe"):
            return redirect(meeting)
        else:
            return render(request, "bbb/roomframe.html", {'meeting': meeting, 'room': room})
    else:
        return render(request, "bbb/notactive.html", {'room': room})

def statsview(request, roomid):
    room = get_object_or_404(Room, id=roomid)
    return HttpResponse(room.get_stats().as_json())

def livestatsview(request, roomid):
    room = get_object_or_404(Room, id=roomid)
    stats = {}
    stats["running"] = room.is_running()
    return HttpResponse(json.dumps(stats))
