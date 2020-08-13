from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'eventpage'
urlpatterns = [
    path('event', views.event_view, name='eventindex'),
]


