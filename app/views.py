from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import *
import bcrypt

# Create your views here.
def index(request):
    return render(request, "index.html")

def register(request):
    if request.method == "POST":
        errors = User.objects.register_validator(request.POST)
        if len(errors[0]) > 0:
            for key, value in errors[0].items():
                messages.error(request, value, extra_tags="register")
            return redirect("/")
        else:
            request.session["user_id"] = errors[1]
            return redirect("/travels")
    else:
        return render(request, "index.html")

def login(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if len(errors[0]) > 0:
            for key, value in errors[0].items():
                messages.error(request, value, extra_tags="login")
            return redirect("/")
        else:
            request.session["user_id"] = errors[1]
            return redirect("/travels")
    else:
        return redirect("/")

def logout(request):
    request.session.clear()
    return redirect("/")

def travels(request):
    if request.session.get("user_id") != None:
        logged_user = User.objects.get(id=request.session["user_id"])
        context = {
            "logged_user": logged_user,
            "trips": Trip.objects.filter(Q(user_planner=logged_user) | Q(user_joined=logged_user)).distinct(),
            "users": User.objects.all().exclude(id=logged_user.id),
            "all_trips": Trip.objects.all()
        }
        print(context["trips"])
        print(Trip.objects.filter(user_joined=logged_user))
        print(Trip.objects.filter(user_planner=logged_user))
        return render(request, "travels.html", context)
    else:
        return redirect("/")

def add(request):
    if request.session.get("user_id") != None:
        logged_user = User.objects.get(id=request.session["user_id"])
        context = {
            "logged_user": logged_user
        }
        return render(request, "add.html", context)
    else:
        return redirect("/")

def add_trip(request):
    if request.session.get("user_id") != None:
        errors = Trip.objects.trip_validator(request.POST)
        print(errors)
        if len(errors):
            for tag, error in errors.items():
                messages.error(request, error)
                return redirect("/add")
        else:
            user_planner = User.objects.get(id=request.session["user_id"])
            Trip.objects.create(destination=request.POST["destination"], description=request.POST["description"], user_planner=user_planner, travel_start=request.POST["travel_start"], travel_end=request.POST["travel_end"])
        return redirect("/travels")
    else:
        return redirect("/")

def show_trip(request, id):
    if request.session.get("user_id") != None:
        user = User.objects.get(id=request.session["user_id"])
        context = {
            "trip": Trip.objects.filter(id=id),
            "joined_users": User.objects.filter(joined_trips=id),
            "user": user
        }
        return render(request, "show_trip.html", context)
    else:
        return redirect("/")

def join(request, id):
    if request.session.get("user_id") != None:
        this_trip = Trip.objects.get(id=id)
        this_trip.user_joined.add(request.session["user_id"])
        this_trip.save()
        return redirect("/travels")
    else:
        return redirect("/")

def home(request):
    return redirect("/travels")