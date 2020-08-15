from django.shortcuts import render
from partners.models import Partner

# landingpage
def index(request):
    context = {}
    context['venue_partners'] = Partner.objects.filter(hide=False, bbb__isnull=False).order_by("order")
    context['venueless_partners'] = Partner.objects.filter(hide=False, bbb__isnull=True).order_by("order") # lul :3

    return render(request, "index.html", context)
