from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.conf import settings
import re

# TODO: translation

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data["username"]
        if len(username) > 23:
            raise ValidationError("Usernames can only consist of 23 characters or less")
        elif username.startswith("guest-"):
            raise ValidationError("Username can not start with guest- prefix")
        elif '<script>' in username:
            raise ValidationError("rly?!")
        elif not re.match(r"^[a-z0-9-_]+$", username):
            raise ValidationError("Username can only consist of lowercase letters and numbers, dashes and underscores :)")
        elif get_user_model().objects.filter(username=username):
            raise ValidationError("User with that username already exists.")

        return cleaned_data

class NameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username = "guest-%s" % cleaned_data["name"]
        if len(cleaned_data["name"]) > 17:
            raise ValidationError("Names can only consist of 17 characters or less")
        elif '<script>' in username:
            raise ValidationError("rly?!")
        elif not re.match(r"^[a-z0-9-_]+$", username):
            raise ValidationError("Names can only consist of lowercase letters and numbers, dashes and underscores :)")

        return cleaned_data
