from django.db import models
from django.contrib.auth import get_user_model
import bbb.models
from markupfield.fields import MarkupField
import urllib.parse

class Partner(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    url = models.URLField(blank=False, null=False)
    logo = models.ImageField(blank=False, null=False, upload_to='partners')

    order = models.IntegerField(default=9000)

    description_de = MarkupField(blank=True, null=True, escape_html=True, default_markup_type='markdown')
    description_en = MarkupField(blank=True, null=True, escape_html=True, default_markup_type='markdown')

    owner = models.ForeignKey(get_user_model(), related_name='owns_partnerinfo', blank=True, null=True, on_delete=models.SET_NULL)
    bbb = models.ForeignKey(bbb.models.Room, related_name='for_partner', blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.description.raw = self.description.raw.replace("javascript:", "nope:")
        return models.Model.save(self, *args, **kwargs)

    def __str__(self):
        return self.name
