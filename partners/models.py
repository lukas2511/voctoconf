from django.db import models
from django.contrib.auth import get_user_model
import bbb.models

class Partner(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    url = models.URLField(blank=False, null=False)
    logo = models.ImageField(blank=False, null=False, upload_to='partners')

    order = models.IntegerField(default=9000)

    description = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(get_user_model(), related_name='owns_partnerinfo', blank=True, null=True, on_delete=models.SET_NULL)
    bbb = models.ForeignKey(bbb.models.Room, related_name='for_partner', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
