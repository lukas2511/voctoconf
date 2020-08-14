from django.shortcuts import render, redirect
from .models import Message
from authstuff.names import name_required

@name_required
def chatview(request, room=None):
    if room is None:
        return redirect("/chat/lobby")

    messages = Message.objects.filter(room=room).order_by('-date')
    if messages:
        backlog = [msg.chatmsg() for msg in messages[:100][::-1]]
    else:
        backlog = []

    return render(request, "chat.html", {'room_name': room, 'backlog': backlog})
