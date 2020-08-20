from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'eventpage'
urlpatterns = [
    path('event', views.event_overview, name='eventoverview'),
    path('stream/<str:roomid>', views.stream_view, name='stream'),
    path('event/<str:eventid>', views.event_view, name='event'),
    path('person/<int:pid>', views.person_view, name='person'),
    path('instructions', views.instructionsview, name='instructions'),
]


