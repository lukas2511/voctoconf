from django.shortcuts import render
from authstuff.names import name_required
from django.http import HttpResponse

@name_required
def event_view(request):
    return HttpResponse(request.username)
