from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'partners'
urlpatterns = [
    path('partner/<str:partnerid>', views.partner_view, name='partner'),
]
