from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Partner

def partner_view(request, partnerid):
    partner = get_object_or_404(Partner, id=partnerid)
    return render(request, "partners/partner.html", {'partner': partner})
