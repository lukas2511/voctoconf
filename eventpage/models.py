from django.db import models
import bbb.models
from django.contrib.auth import get_user_model

class Track(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=100)
    bbb = models.OneToOneField(bbb.models.Room, blank=True, null=True, related_name='schedule_room', on_delete=models.SET_NULL)
    view_size = models.IntegerField(default=4)
    order = models.IntegerField(default=9000)
    hide = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    name_modified = models.BooleanField(default=False)

    user = models.OneToOneField(get_user_model(), related_name='speaker', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "%d: %s" % (self.id, self.name)

class Event(models.Model):
    id = models.IntegerField(primary_key=True)

    hide = models.BooleanField(default=False)
    bbb = models.ForeignKey(bbb.models.Room, blank=True, null=True, related_name='schedule_events', on_delete=models.SET_NULL)

    date = models.DateTimeField()
    date_modified = models.BooleanField(default=False)

    duration = models.IntegerField("Duration (seconds)", default=1800)
    duration_modified = models.BooleanField(default=False)

    title = models.CharField(max_length=200, blank=False, null=False)
    title_modified = models.BooleanField(default=False)

    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=False)
    room_modified = models.BooleanField(default=False)

    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=False)
    track_modified = models.BooleanField(default=False)

    persons = models.ManyToManyField(Person, related_name='holding', blank=True)
    persons_modified = models.BooleanField(default=False)

    evtype = models.CharField(max_length=200, blank=False, null=False)
    evtype_modified = models.BooleanField(default=False)

    def persons_str(self):
        persons = [p.name for p in self.persons.all()]
        return ", ".join(persons)

    def __str__(self):
        return "%d: %s" % (self.id, self.title)
