from django.shortcuts import render

# Create your views here.


def instructions_view(request):
    key = request.GET.get("key")
    return render(request, "instructions.html", {'key': key})

def privacy_policy_view(request):
    key = request.GET.get("key")
    return render(request, "privacy_policy.html", {'key': key})