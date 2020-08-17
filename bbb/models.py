from django.db import models
from django.contrib.auth import get_user_model
import secrets
import os
import base64
import uuid
import urllib.parse
import hashlib
import requests
import xmltodict
import traceback
import random
import json
from django.conf import settings
from helpers.models import lock

def bbb_apiurl(url, secret, apicall, params):
    urlparams = urllib.parse.urlencode(params)
    checksum = hashlib.sha1((apicall + urlparams + secret).encode()).hexdigest()
    if urlparams: urlparams += "&"
    urlparams += "checksum=%s" % checksum

    return "%s%sapi/%s?%s" % (url, "?" if not url.endswith("/") else "", apicall, urlparams)

def bbb_apicall(url, secret, apicall, params, post_data=None):
    if post_data is not None:
        ret = requests.post(bbb_apiurl(url, secret, apicall, params), data=post_data, allow_redirects=False, timeout=5)
    else:
        ret = requests.get(bbb_apiurl(url, secret, apicall, params), allow_redirects=False, timeout=5)
    response = xmltodict.parse(ret.text)
    return response["response"]

class Server(models.Model):
    url = models.URLField(blank=False, null=False)
    secret = models.CharField(max_length=200, blank=False, null=False)

    for_workshops = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'BigBlueButton Server'

    def get_secret(self):
        if os.path.exists(self.get_secretfile()):
            return open(self.get_secretfile(), "r").read()
        else:
            raise Exception("no secret for bbb host %s found" % self.url)

    def get_secretfile(self):
        return os.path.join(settings.BBB_SECRETS_DIR, base64.urlsafe_b64encode(self.url.encode()).decode())

    def save(self, *args, **kwargs):
        if self.secret and self.secret != "stored-safely-in-file-do-not-edit-this-string":
            open(self.get_secretfile(), "w").write(self.secret)
            self.secret = "stored-safely-in-file-do-not-edit-this-string"
        models.Model.save(self, *args, **kwargs)

    def __str__(self):
        return "%s (ID: %d)" % (self.url.split("/")[2], self.id)

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(max_length=35, blank=True, null=True)

    server = models.ForeignKey(Server, blank=False, null=False, on_delete=models.CASCADE)
    moderators = models.ManyToManyField(get_user_model(), related_name='moderating', blank=True)
    welcome_msg = models.TextField("Welcome message", blank=True, null=True)
    max_participants = models.IntegerField(default=100, blank=False, null=False)
    record = models.BooleanField(null=False, blank=False, default=False)
    logo = models.ImageField('Room branding', upload_to="room-logos", blank=True, null=True)
    slides = models.FileField('Default slides', upload_to="room-logos", blank=True, null=True)

    start_as_guest = models.BooleanField("Allow guests to start the conference", null=False, blank=False, default=False)

    yolomode = models.BooleanField("Everybody is moderator", default=False)
    mute_on_start = models.BooleanField("Join muted", null=False, blank=False, default=True)
    lock_mics = models.BooleanField("Lock microphones", null=False, blank=False, default=False)
    lock_cams = models.BooleanField("Lock cameras", null=False, blank=False, default=False)
    lock_private_chat = models.BooleanField("Lock private chat", null=False, blank=False, default=False)
    lock_public_chat = models.BooleanField("Lock public chat", null=False, blank=False, default=False)
    lock_shared_notes = models.BooleanField("Lock shared notes", null=False, blank=False, default=False)
    lock_layout = models.BooleanField("Lock layout", null=False, blank=False, default=False)

    moderator_pw = models.CharField(max_length=100, blank=True, null=True)
    attendee_pw = models.CharField(max_length=100, blank=True, null=True)

    hangout_room = models.BooleanField(default=False)

    guest_policy = models.CharField("Guest policy", null=False, blank=False, default='ALWAYS_ACCEPT', choices=(('ALWAYS_ACCEPT', 'Always accept'), ('ALWAYS_DENY', 'Always deny'), ('ASK_MODERATOR', 'Ask moderator')), max_length=30)

    def lock_str(self):
        locked = []
        if self.lock_mics: locked.append("mic")
        if self.lock_cams: locked.append("cam")
        if self.lock_private_chat: locked.append("privchat")
        if self.lock_public_chat: locked.append("pubchat")
        if self.lock_shared_notes: locked.append("notes")
        if self.lock_layout: locked.append("layout")
        return ", ".join(locked)

    class Meta:
        verbose_name = 'BigBlueButton Room'

    def link(self):
        if self.slug:
            return "/bbb/%s" % self.slug
        else:
            return "/bbb/%s" % self.id

    def get_stats(self):
        try:
            return self.stats.all().latest('date')
        except:
            return None

    def __str__(self):
        return "%s on %s" % (self.name, self.server)

    def is_moderator(self, user):
        if self.yolomode:
            return True

        if not user.is_authenticated:
            return False

        if user.is_superuser or user.is_staff:
            return True

        if self.moderators.filter(username=user.username).exists():
            return True

        if self.for_partner.all() and any([(x.owner and x.owner == user) for x in self.for_partner.all()]):
            return True

        return False

    def get_moderators(self):
        return self.moderators.all() + self.for_sponsorinfo.all()

    def get_logo(self):
        partner = self.for_partner.all()[0] if self.for_partner.all() else None
        if self.logo:
            return self.logo
        elif partner and partner.logo:
            return partner.logo
        else:
            return None

    def join(self, request=None, name=None, as_moderator=None):
        with lock("bbbroom-%s" % self.id):
            if as_moderator is None:
                if request:
                    as_moderator = self.is_moderator(request.user)
                else:
                    as_moderator = False

            meetinginfo = self.api_meetinginfo()
            if meetinginfo["running"] == "false":
                if not as_moderator and not self.start_as_guest:
                    return False

                if "meetingID" not in meetinginfo:
                    meetinginfo = self.api_create()

            params = {}
            params['meetingID'] = self.id
            params['password'] = meetinginfo['moderatorPW'] if as_moderator else meetinginfo['attendeePW']
            params['createTime'] = meetinginfo['createTime']
            if request and request.user.is_authenticated:
                params['fullName'] = request.user.username
                params['userID'] = request.user.id
            elif name is not None:
                params['fullName'] = name
            else:
                params['fullName'] = 'guest%d' % random.randrange(100000)

            params['guest'] = 'false' if as_moderator else 'true'
            params['redirect'] = "true"
            params['joinViaHtml5'] = "false"
            return bbb_apiurl(self.server.url, self.server.get_secret(), "join", params)

    def is_running(self):
        return self.api_isrunning()

    # api functions
    def api_meetinginfo(self):
        ret = bbb_apicall(self.server.url, self.server.get_secret(), "getMeetingInfo", {"meetingID": self.id})
        if ret["returncode"] != "SUCCESS":
            if self.api_isrunning():
                raise Exception("something went wrong querying meeting information from bbb server")
            else:
                ret = {'running': 'false'}
        return ret

    def api_isrunning(self):
        return (bbb_apicall(self.server.url, self.server.get_secret(), "isMeetingRunning", {"meetingID": self.id})['running'] == "true")

    def api_end(self):
        meetinginfo = self.api_meetinginfo()
        if 'moderatorPW' not in meetinginfo:
            return True
        params = {}
        params['meetingID'] = self.id
        params['password'] = meetinginfo['moderatorPW']
        return (bbb_apicall(self.server.url, self.server.get_secret(), "end", params)['returncode'] == 'SUCCESS')

    def api_create(self):
        self.save()
        params = {}
        params['meetingID'] = self.id
        params['name'] = self.name
        params['attendeePW'] = secrets.token_urlsafe(16)
        params['moderatorPW'] = secrets.token_urlsafe(16)
        if self.welcome_msg:
            params['welcome'] = self.welcome_msg
        params['maxParticipants'] = self.max_participants
        params['record'] = 'true' if self.record else 'false'
        params['meta_foobar'] = 'fnord'
        params['autoStartRecording'] = "true"
        params['allowStartStopRecording'] = "false"
        params['logoutURL'] = "https://%s/bbb/%s?ended=1" % (settings.DOMAIN, self.id)
        logo = self.get_logo()
        if logo:
            params['logo'] = logo.url

        params['muteOnStart'] = "true" if self.mute_on_start else "false"
        params['lockSettingsDisableCam'] = "true" if self.lock_cams else "false"
        params['lockSettingsDisableMic'] = "true" if self.lock_mics else "false"
        params['lockSettingsDisablePrivateChat'] = "true" if self.lock_private_chat else "false"
        params['lockSettingsDisablePublicChat'] = "true" if self.lock_public_chat else "false"
        params['lockSettingsDisableNote'] = "true" if self.lock_shared_notes else "false"
        params['lockSettingsLockedLayout'] = "true" if self.lock_layout else "false"
        params['guestPolicy'] = self.guest_policy

        post_data = None
        if self.slides:
            post_data = '<modules>'
            post_data += '<module name="presentation">'
            post_data += '<document url="%s" filename="default.pdf"/>' % self.slides.url
            post_data += '</module>'
            post_data += '</modules>'
            print(post_data)

        return bbb_apicall(self.server.url, self.server.get_secret(), "create", params, post_data)

class RoomStats(models.Model):
    room = models.ForeignKey(Room, related_name='stats', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    running = models.BooleanField()
    moderators = models.IntegerField(default=0)
    participants = models.IntegerField(default=0)
    presenter = models.CharField(max_length=100, blank=True, default="")

    recording = models.BooleanField(default=False)
    voiceparticipants = models.IntegerField(default=0)
    listeners = models.IntegerField(default=0)
    videocount = models.IntegerField(default=0)

    creation_date = models.DateTimeField(blank=True, null=True)

    def as_json(self):
        stats = {}
        stats['date'] = str(self.date)
        stats['running'] = self.running
        stats['moderators'] = self.moderators
        stats['participants'] = self.participants
        stats['presenter'] = self.presenter
        stats['recording'] = self.recording
        stats['voiceparticipants'] = self.voiceparticipants
        stats['listeners'] = self.listeners
        stats['videocount'] = self.videocount
        return json.dumps(stats)

    def __str__(self):
        return "Stats for %s (Collected: %s)" % (self.room.name, self.date)
