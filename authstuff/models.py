from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

class User(AbstractUser):
    pass

def validate_token(token):
    if len(token) != 42:
        raise ValidationError('Token length must be exactly 42 characters')

def generate_token():
    return get_random_string(42)

class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=42, validators=[validate_token], default=generate_token)

    def __str__(self):
        return self.user.username
