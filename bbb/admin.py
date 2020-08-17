from django.contrib import admin
from .models import Server, Room, RoomStats

admin.site.register(Server)

class RoomAdmin(admin.ModelAdmin):
    autocomplete_fields = ['moderators']
    readonly_fields = ['id']
    fieldsets = (
        ('Basics', {'fields': ('id', 'name', 'slug', 'server', 'record')}),
        ('Visibility', {'fields': ('hangout_room', )}),
        ('Joining', {'fields': ('moderators', 'guest_policy', 'max_participants', 'mute_on_start', 'start_as_guest')}),
        ('Branding', {'fields': ('logo', 'welcome_msg', 'slides')}),
        ('Lockdown', {'fields': ('lock_cams', 'lock_mics', 'lock_private_chat', 'lock_public_chat', 'lock_shared_notes', 'lock_layout')}),
    )

admin.site.register(Room, RoomAdmin)

class RoomStatsAdmin(admin.ModelAdmin):
    readonly_fields = ['room', 'date', 'running', 'moderators', 'participants', 'presenter', 'recording', 'voiceparticipants', 'listeners', 'videocount', 'creation_date']

admin.site.register(RoomStats, RoomStatsAdmin)
