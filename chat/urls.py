from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('chat', views.chatview),
    path('chat/<str:room>', views.chatview),
]
