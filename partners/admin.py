from django.contrib import admin
from .models import Partner

class PartnerAdmin(admin.ModelAdmin):
    autocomplete_fields = ["owner"]
    fieldsets = (
        ('Details', {
            'fields': ('name', 'url', 'logo', 'description_de', 'description_en')
        }),
        ('Order override', {
            'fields': ('order', )
        }),
        ('Connections', {
            'fields': ('owner', 'bbb', )
        }),
    )

admin.site.register(Partner, PartnerAdmin)
