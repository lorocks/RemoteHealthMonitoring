from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import *
from django.shortcuts import render
from django.urls import reverse

# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return render(request,"login.html",{"message": None})
    message = {
        "message":"Logged in Yay"
    }
    return render(request,"index.html",message)

def logout_view(request):
    logout(request)
    return render(request,"login.html",{"message":"Logged out"})

def login_view(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "login.html", {"message": "Invalid credentials."})

    #make all request post and put if request.method==post else raise http404("invalid")