from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Partner
from .forms import PartnerForm

def partner_view(request, partnerid):
    partner = get_object_or_404(Partner, id=partnerid)

    form = None
    if request.user.is_authenticated and (request.user == partner.owner or request.user.is_superuser):
        if request.method == 'POST':
            form = PartnerForm(request.POST)
            if form.is_valid():
                partner.description_de = form.cleaned_data['description_de']
                partner.description_en = form.cleaned_data['description_en']
                partner.save()
                return redirect("/partner/%d?saved=1" % partner.id)

        form = PartnerForm(initial={'description_de': partner.description_de, 'description_en': partner.description_en})

    return render(request, "partners/partner.html", {'partner': partner, 'form': form})
