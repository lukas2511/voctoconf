from django.shortcuts import redirect
from urllib.parse import quote

def name_required(function):
    def wrapper(request, *args, **kw):
        if request.username:
            return function(request, *args, **kw)
        else:
            return redirect("/setname?next=%s" % quote(request.get_full_path()))
    return wrapper
