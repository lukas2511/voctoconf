from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
import traceback
from .forms import LoginForm, RegisterForm, NameForm

def logout_view(request):
    request.session["name"] = None
    if request.user.is_authenticated:
        logout(request)
    return redirect("/event")

def setname_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") if request.GET.get("next") is not None else "/event")

    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            request.session["name"] = form.cleaned_data["name"]
            return redirect(request.GET.get("next") if request.GET.get("next") is not None else "/event")
    else:
        if 'name' in request.session:
            form = NameForm(initial={'name': request.session['name']})
        else:
            form = NameForm()

    return render(request, "accounts/setname.html", {"form": form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") if request.GET.get("next") is not None else "/event")

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = get_user_model()()
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.username = form.cleaned_data["username"]
            user.email = ""
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect(request.GET.get("next") if request.GET.get("next") is not None else "/event")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") if request.GET.get("next") is not None else "/event")

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
                if user and user.is_active:
                    login(request, user)
                    return redirect(request.GET.get("next") if request.GET.get("next") is not None else "/event")
                else:
                    form.add_error(None, "Please enter a correct username and password.\nNote that both fields may be case-sensitive.")
            except:
                form.add_error(None, "An exception occured during authentication... this is weird... we're looking into it...")
                traceback.print_exc()
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {'form': form})


