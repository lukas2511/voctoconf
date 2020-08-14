from django.shortcuts import render
from partners.models import Partner

# landingpage
def index(request):
    partners = Partner.objects.filter(hide=False).order_by("order")
    return render(request, "index.html", {'partners': partners})


