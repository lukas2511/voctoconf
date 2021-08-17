from django.core.management.base import BaseCommand, CommandError
from bbb.models import Server, Room, RoomStats
from django.utils import timezone
import requests
import json
import dateutil.parser
import traceback
import time
import datetime

class Command(BaseCommand):
    help = 'Remove old room statistics'

    def handle(self, *args, **options):
        onehourago = timezone.now() - datetime.timedelta(hours=1)
        objs = RoomStats.objects.filter(date__lte=onehourago)
        if objs.exists():
            objs.delete()
