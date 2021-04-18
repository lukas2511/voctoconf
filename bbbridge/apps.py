from django.apps import AppConfig
from bbb.models import room_opened, Room
from django.dispatch import receiver
from threading import Thread
import json
import logging
import asyncio
import requests
import websockets
import secrets

class BBBridgeConfig(AppConfig):
    name = 'bbbridge'

@receiver(room_opened)
def on_room_opened(sender, room: Room):
    start_bridge(room.join(name='bbbride'))

def start_bridge(room_name: str, api_url: str):
    ChatBridge(room_name, api_url).start()

def unasyncio(method):
    return asyncio.get_event_loop().run_until_complete(method)

class ChatBridge(Thread):
    def __init__(self, room_name: str, join_url: str):
        self.listeners = []
        self.join_url = join_url
        self.room_name = room_name
        self.logger = logging.getLogger(f"BBBridge/{room_name}")
        self.running = True
        self.ready = False
        Thread.__init__(self, daemon=True)
        self.users = {}

    def get_user_by_internal_id(self, userid):
        for user in self.users.values():
            if user['userId'] == userid:
                return user
        return None

    def join(self, join_url):
        tmpsession = requests.session()
        req = tmpsession.get(join_url, allow_redirects=False)

        self.logger.debug("Got join url: %s?..." % join_url.split("?")[0])

        self.bbb_server = '/'.join(req.headers['Location'].split('/')[:3])
        self.bbb_token = req.headers['Location'].split('?sessionToken=')[1]
        self.bbb_info = json.loads(tmpsession.get(self.bbb_server + "/bigbluebutton/api/enter?sessionToken=" + self.bbb_token).text)["response"]

    def connect(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.logger.debug("Connecting to websocket")
        self.websocket = unasyncio(websockets.connect(self.bbb_server.replace("https", "wss") + "/html5client/sockjs/494/" + secrets.token_urlsafe(8) + "/websocket"))

        _ = self.recv()
        _ = self.recv()
        self.logger.debug("Sending initial control messages")
        self.send({'msg': 'connect', 'version': '1', 'support': ['1', 'pre1', 'pre2']})
        self.send({'msg': 'method', 'method': 'userChangedLocalSettings', 'params': [{'application': {'animations': True, 'chatAudioAlerts': False, 'chatPushAlerts': False, 'fallbackLocale': 'en', 'overrideLocale': None, 'userJoinAudioAlerts': False, 'userJoinPushAlerts': False, 'locale': 'en-US'}, 'audio': {'inputDeviceId': 'undefined', 'outputDeviceId': 'undefined'}, 'dataSaving': {'viewParticipantsWebcams': False, 'viewScreenshare': False}}], 'id': '1'})
        self.send({'msg': 'method', 'method': 'validateAuthToken', 'params': [self.bbb_info['meetingID'], self.bbb_info['internalUserID'], self.bbb_info['authToken'], self.bbb_info['externUserID']], 'id': '2'})

        subscription_token = secrets.token_hex(8)
        #for sub in ['annotations', 'breakouts', 'captions', 'current-user', 'group-chat', 'group-chat-msg', 'guestUser', 'local-settings', 'meetings', 'meetings', 'meeting-time-remaining', 'meteor_autoupdate_clientVersions', 'network-information', 'note', 'ping-pong', 'polls', 'presentation-pods', 'presentations', 'record-meetings', 'screenshare', 'slide-positions', 'slides', 'users', 'users-infos', 'users-settings', 'video-streams', 'voice-call-states', 'voiceUsers', 'whiteboard-multi-user']:
        for sub in ['current-user', 'group-chat', 'group-chat-msg', 'ping-png']:
            self.logger.debug("Subscribing to %s messages" % sub)
            self.send({'msg': 'sub', 'id': f"bbbridge-${subscription_token}-sub", 'name': sub, 'params': []})

    def run(self):
        self.join(self.join_url)
        self.connect()
        while self.running:
            msg = self.recv()

            if not self.ready and msg['msg'] == 'ready':
                self.ready = True
                self.logger.debug("Session manager is ready")

            for listener in self.listeners:
                listener(msg)

            if msg['msg'] == 'ping':
                self.logger.debug("Responding to ping")
                self.send({'msg': 'pong'})

            if 'collection' not in msg:
                continue

            if msg['collection'] == 'users':
                if msg['msg'] == 'added':
                    self.users[msg['id']] = msg['fields']
                    self.users[msg['id']]['_id'] = msg['id']
                elif msg['msg'] == 'changed':
                    self.users[msg['id']].update(msg['fields'])

    def recv(self):
        raw = unasyncio(self.websocket.recv())
        if raw.startswith('a['):
            return json.loads(json.loads(raw[1:])[0])
        else:
            return raw

    def send(self, msg):
        raw = unasyncio(self.websocket.send(json.dumps([json.dumps(msg)])))