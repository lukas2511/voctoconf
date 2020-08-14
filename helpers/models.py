from django.db import models
from contextlib import contextmanager
from django.db.transaction import atomic

class ThreadSafe(models.Model):
    key = models.CharField(max_length=80, unique=True)

@contextmanager
def lock(key):
    pk = ThreadSafe.objects.get_or_create(key=key)[0].pk
    try:
        objs = ThreadSafe.objects.filter(pk=pk).select_for_update()
        with atomic():
            list(objs)
            yield None
    finally:
        pass

class StaticPage(models.Model):
    name = models.CharField(max_length=100)
    text_de = models.TextField(blank=True, null=True)
    text_en = models.TextField(blank=True, null=True)

    def text(self, locale="de"):
        if locale == "de" and self.text_de:
            return self.text_de
        elif locale == "en" and self.text_en:
            return self.text_en
        elif self.text_de:
            return self.text_de
        else:
            return self.text_en

    def __str__(self):
        return self.name
