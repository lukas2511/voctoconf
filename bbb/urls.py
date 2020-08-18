from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('bbb/<str:roomid>', views.roomview),
    path('bbb/<str:roomid>/stats.json', views.statsview),
    path('bbb/<str:roomid>/setlive', views.setliveview),
    path('bbb/<str:roomid>/livestats.json', views.livestatsview),
]
