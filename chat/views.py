from os import name
from django.shortcuts import render, redirect
from .models import Message
from authstuff.names import name_required
from .helpers import is_chat_moderator
from .models import Connections


@name_required
def chatview(request, room=None):
    if room is None:
        return redirect("/chat/lobby")

    messages = Message.get_message_jsons(room, 100)
    if messages:
        backlog = [*messages]
    else:
        backlog = []

    return render(request, "chat/chat.html", {
        'room_name': room,
        # @TODO: implement guest name
        'chat_settings': { 
            'user_name': request.username,
            'room_name': room,
            'backlog': backlog },
        'is_chat_moderator': is_chat_moderator(request.user),
        'usercount': Connections.count(room_name=room)
    })

