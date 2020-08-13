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
