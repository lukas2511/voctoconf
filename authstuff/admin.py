from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models

class CustomUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        fieldsets = []
        fieldsets += [(None, {'fields': ('username', 'password', 'is_active')})]
        fieldsets += [('Optional', {'fields': ('email', )})]

        fieldsets += (
            ('Personal info', {'fields': ('first_name', 'last_name',)}),
            ('Permissions', {'fields': ('is_staff', 'is_superuser', )}),
            ('Important dates', {'fields': ('date_joined', 'last_login',)}),
        )

        return fieldsets

admin.site.register(models.User, CustomUserAdmin)

admin.site.register(models.AuthToken)

