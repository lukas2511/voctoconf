from django.shortcuts import render, redirect
from .models import Message
from authstuff.names import name_required
from .helpers import is_chat_moderator
from .models import Connection

@name_required
def chatview(request, room=None):
    if room is None:
        return redirect("/chat/lobby")

    messages = Message.getMessages(room, 100)
    if messages:
        backlog = [msg.to_json() for msg in messages]
    else:
        backlog = []

    return render(request, "chat/chat.html", {
        'room_name': room,
        'user_name': request.user.username if request.user.is_authenticated else '', # @TODO: implement guest name
        'backlog': backlog,
        'is_chat_moderator': is_chat_moderator(request.user),
        'usercount': Connection.count(room_name = room)
    })
