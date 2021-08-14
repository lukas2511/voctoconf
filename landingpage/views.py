from django.shortcuts import render
from partners.models import Partner
from django.conf import settings

# landingpage
def index(request):
    context = {}
    context['venue_partners'] = Partner.objects.filter(hide=False, is_project=False, bbb__isnull=False).order_by("order")
    context['venueless_partners'] = Partner.objects.filter(hide=False, is_project=False, bbb__isnull=True).order_by("order") # lul :3
    context['page_live'] = settings.PAGE_LIVE or (request.GET.get("preview") is not None)

    return render(request, "landingpage/index.html", context)
