from django.db import models
from django.contrib.auth import get_user_model
import bbb.models
import urllib.parse
import html
import bleach
import markdown
from sorl.thumbnail import ImageField

def parse_markdown(text):
    html = markdown.markdown(text, extensions=['nl2br'])
    allowed_tags = {
        'br': [],
        'b': [],
        'em': [],
        'i': [],
        'p': [],
        'a': ['href'],
        'code': ['class'],
        'pre': [],
        'blockquote': [],
        'hr': [],
        'strong': [],
        'h1': [],
        'h2': [],
        'h3': [],
        'h4': [],
        'h5': [],
        'h6': [],
        'ol': [],
        'ul': [],
        'li': [],
        'img': ['src', 'alt'],
    }
    return bleach.clean(html, tags=allowed_tags.keys(), attributes=allowed_tags)

class Partner(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(max_length=35, blank=True, null=True)

    url = models.URLField(blank=False, null=False)
    logo = ImageField(blank=False, null=False, upload_to='partners')
    is_project = models.BooleanField(default=False, null=False, blank=False)

    hide = models.BooleanField(default=False)

    order = models.IntegerField(default=9000)

    description_de = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)

    description_de_html = models.TextField(blank=True, null=True)
    description_en_html = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(get_user_model(), related_name='owns_partnerinfo', blank=True, null=True, on_delete=models.SET_NULL)
    bbb = models.ForeignKey(bbb.models.Room, related_name='for_partner', blank=True, null=True, on_delete=models.SET_NULL)

    def link(self):
        if self.slug:
            return "/partner/%s" % self.slug
        else:
            return "/partner/%s" % self.id

    def has_description_or_room(self):
        if self.description_de:
            return True
        if self.description_en:
            return True
        if self.bbb:
            return True
        return False

    def save(self, *args, **kwargs):
        self.description_de_html = parse_markdown(self.description_de)
        self.description_en_html = parse_markdown(self.description_en)

        return models.Model.save(self, *args, **kwargs)

    def __str__(self):
        return self.name
