from django.contrib import admin
from .models import Server, Room

admin.site.register(Server)

class RoomAdmin(admin.ModelAdmin):
    autocomplete_fields = ['moderators']
    fieldsets = (
        ('Basics', {'fields': ('name', 'server')}),
        ('Joining', {'fields': ('moderators', 'guest_policy', 'max_participants', 'mute_on_start', 'start_as_guest')}),
        ('Branding', {'fields': ('logo', 'welcome_msg')}),
        ('Lockdown', {'fields': ('lock_cams', 'lock_mics', 'lock_private_chat', 'lock_public_chat', 'lock_shared_notes', 'lock_layout')}),
    )

admin.site.register(Room, RoomAdmin)
