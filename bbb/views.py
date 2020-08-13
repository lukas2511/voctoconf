from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from .models import Room
from authstuff.names import name_required

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
            return render(request, "bbb/roomframe.html", {'meeting': meeting})
    else:
        return render(request, "bbb/notactive.html")

