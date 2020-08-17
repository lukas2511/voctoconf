from django.contrib import admin
from .models import Room, Person, Event, Track, Announcement

class TrackAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Track, TrackAdmin)

class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'bbb', 'stream']

admin.site.register(Room, RoomAdmin)

class PersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['id', 'name']

admin.site.register(Person, PersonAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    autocomplete_fields = ['persons']

admin.site.register(Event, EventAdmin)

admin.site.register(Announcement)
