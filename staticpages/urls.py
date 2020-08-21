from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'eventpage'
urlpatterns = [
    path('privacy', views.privacy_policy_view, name='privacy policy'),
    path('instructions', views.instructions_view, name='instructions'),
]


