from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('bbb/<str:roomid>', views.roomview),
    path('bbb/<str:roomid>/stats.json', views.statsview),
]
