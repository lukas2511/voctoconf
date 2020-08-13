from django.shortcuts import render

def chatview(request):
    return render(request, "chat.html")
