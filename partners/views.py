from django.shortcuts import render, redirect, get_object_or_404
from .models import Partner
from .forms import PartnerForm
from django.http import Http404

def get_partner(roomid: str):
    if roomid.isdigit():
        return get_object_or_404(Partner, id=int(roomid))
    elif roomid:
        return get_object_or_404(Partner, slug=roomid)
    else:
        raise Http404("No room found")

def partner_view(request, partnerid: str):
    partner = get_partner(partnerid)

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
