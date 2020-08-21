from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.views import static
from django.conf.urls.static import static
from django.conf.urls.i18n import urlpatterns as i18n_urlpatterns
import landingpage.urls
import chat.urls
import bbb.urls
import authstuff.urls
import eventpage.urls
import partners.urls
import staticpages.urls

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_urlpatterns

if settings.DEBUG:
    urlpatterns += static('/media', document_root=settings.MEDIA_ROOT)

urlpatterns += landingpage.urls.urlpatterns
urlpatterns += chat.urls.urlpatterns
urlpatterns += bbb.urls.urlpatterns
urlpatterns += authstuff.urls.urlpatterns
urlpatterns += eventpage.urls.urlpatterns
urlpatterns += partners.urls.urlpatterns
urlpatterns += staticpages.urls.urlpatterns
