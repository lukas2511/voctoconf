from django.shortcuts import render
from partners.models import Partner

# landingpage
def index(request):
    partners = Partner.objects.filter(hide=False).order_by("order")
    return render(
        request,
        "index.html",
        {
            'venue_partners': [partner for partner in partners if partner.bbb],
            'venueless_partners': [partner for partner in partners if not partner.bbb] # lul :3
        })


