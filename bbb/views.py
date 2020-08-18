from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from .models import Room
from authstuff.names import name_required
from django.http import HttpResponse, Http404
import json

def get_room(roomid):
    if len(roomid) == 36:
        return get_object_or_404(Room, id=roomid)
    elif roomid:
        return get_object_or_404(Room, slug=roomid)
    else:
        raise Http404("No room found")

@name_required
def roomview(request, roomid):
    room = get_room(roomid)

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
    room = get_room(roomid)
    return HttpResponse(room.get_stats().as_json())

def livestatsview(request, roomid):
    room = get_room(roomid)
    stats = {}
    stats["running"] = room.is_running()
    stats["live"] = room.live
    return HttpResponse(json.dumps(stats))

def setliveview(request, roomid):
    room = get_room(roomid)
    if request.method == "POST" and room.is_moderator(request.user):
        room.live = (request.POST.get("live") == "1")
        room.save()
        return redirect("%s/setlive?saved=1" % room.link())
    else:
        return render(request, "bbb/streamcontrol.html", {'room': room, 'saved': request.GET.get('saved')})

