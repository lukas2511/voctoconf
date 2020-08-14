from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
import re

class PartnerForm(forms.Form):
    description_de = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    description_de.required = False
    description_en = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    description_en.required = False


