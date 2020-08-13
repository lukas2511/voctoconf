from django.shortcuts import render
from partners.models import Partner

# landingpage
def index(request):
    partners = Partner.objects.all().order_by("order")
    return render(request, "index.html", {'partners': partners})


