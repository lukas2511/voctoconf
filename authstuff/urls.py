from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'authstuff'
urlpatterns = [
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('setname', views.setname_view, name='setname'),
]

