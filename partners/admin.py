from django.contrib import admin
from .models import Partner

class PartnerAdmin(admin.ModelAdmin):
    autocomplete_fields = ["owner"]
    list_display = ('name', 'is_project')
    fieldsets = (
        ('Details', {
            'fields': ('name', 'slug', 'hide', 'is_project', 'url', 'logo', 'description_de', 'description_en')
        }),
        ('Order override', {
            'fields': ('order', )
        }),
        ('Connections', {
            'fields': ('owner', 'bbb', )
        }),
    )

admin.site.register(Partner, PartnerAdmin)
