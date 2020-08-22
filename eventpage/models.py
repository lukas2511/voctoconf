from django.db import models
import bbb.models
from django.contrib.auth import get_user_model
from django.utils.timezone import utc
import datetime
import html

class Track(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    ident = models.CharField('Identification (visible to admin only)', blank=False, null=False, max_length=250)
    html = models.TextField(blank=False, null=False)
    hide = models.BooleanField(default=False)

    def __str__(self):
        return self.ident

class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=35, blank=True, null=True)
    bbb = models.OneToOneField(bbb.models.Room, blank=True, null=True, related_name='schedule_room', on_delete=models.SET_NULL)
    stream = models.CharField("HLS Stream URL", max_length=300, blank=True, null=True)
    stream_moreformats = models.CharField("Link to page with more streaming formats", max_length=300, blank=True, null=True)
    view_size = models.IntegerField(default=4)
    order = models.IntegerField(default=9000)
    hide = models.BooleanField(default=False)

    def link(self):
        if self.stream:
            if self.slug:
                return "/stream/%s" % self.slug
            else:
                return "/stream/%d" % self.id
        elif self.bbb:
            return self.bbb.link()
        else:
            return '#'

    def current_event(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        events = self.events.filter(start__lte=now, end__gte=now).order_by('-start')
        if events:
            return events[0]

    def next_event(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        events = self.events.filter(start__gte=now).order_by('start')
        if events:
            return events[0]

    def __str__(self):
        return self.name

class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    custom = models.BooleanField("Ignore any overrides from schedule", default=False)

    name = models.CharField(max_length=100)
    name_modified = models.BooleanField(default=False)

    image = models.CharField(max_length=200, blank=True, null=True)
    image_modified = models.BooleanField(default=False)

    abstract = models.TextField(blank=True, null=True)
    abstract_modified = models.BooleanField(default=False)

    description = models.TextField(blank=True, null=True)
    description_modified = models.BooleanField(default=False)

    user = models.OneToOneField(get_user_model(), related_name='speaker', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "%d: %s" % (self.id, self.name)

class Event(models.Model):
    id = models.IntegerField(primary_key=True)

    custom = models.BooleanField("Ignore any overrides from schedule", default=False)

    slug = models.SlugField(max_length=200, blank=True, null=True)
    slug_modified = models.BooleanField(default=False)
    
    hide = models.BooleanField(default=False)
    bbb = models.ForeignKey(bbb.models.Room, blank=True, null=True, related_name='events', on_delete=models.SET_NULL)

    start = models.DateTimeField()
    start_modified = models.BooleanField(default=False)

    end = models.DateTimeField()
    end_modified = models.BooleanField(default=False)

    title = models.CharField(max_length=200, blank=False, null=False)
    title_modified = models.BooleanField(default=False)

    logo = models.CharField(max_length=200, blank=True, null=True)
    logo_modified = models.BooleanField(default=False)

    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=False, related_name='events')
    room_modified = models.BooleanField(default=False)

    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=False)
    track_modified = models.BooleanField(default=False)

    persons = models.ManyToManyField(Person, related_name='holding', blank=True)
    persons_modified = models.BooleanField(default=False)

    evtype = models.CharField(max_length=200, blank=False, null=False)
    evtype_modified = models.BooleanField(default=False)

    abstract = models.TextField(blank=True, null=True)
    abstract_modified = models.BooleanField(default=False)

    description = models.TextField(blank=True, null=True)
    description_modified = models.BooleanField(default=False)

    def link(self):
        if self.slug:
            return "/event/%s" % self.slug
        else:
            return "/event/%s" % self.id

    def persons_str(self):
        persons = [p.name for p in self.persons.all()]
        return ", ".join(persons)

    def persons_html(self):
        persons = ['<a href="/person/%d">%s</a>' % (p.id, html.escape(p.name)) for p in self.persons.all()]
        return ", ".join(persons)

    def __str__(self):
        return "%d: %s" % (self.id, self.title)