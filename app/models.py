from django.db import models
from datetime import datetime
import bcrypt
import re

# Create your models here.
class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = [{}, None]
        if len(postData["first_name"]) < 2:
            errors[0]["first_name"] = "» Name has to be at least 2 characters, thank you so much"
        if len(postData["last_name"]) < 2:
            errors[0]["last_name"] = "» Name has to be at least 2 characters, thank you so much"
        if len(postData["username"]) < 3:
            errors[0]["username"] = "» Username has to be at least 3 characters, thank you so much"
        else:
            user_list = User.objects.filter(username=postData["username"])
            if len(user_list) > 0:
                errors[0]["username"] = "» Username is taken, choose a different one, thank you so much"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData["email"]):
            errors[0]["email"] = "» That email is invalid"
        else:
            user_list = User.objects.filter(email=postData["email"].upper())
            if len(user_list) > 0:
                errors[0]["email"] = "» Email is taken, choose a different one, thank you so much"
        if len(postData["password"]) < 8:
            errors[0]["password"] = "» Password has to be at least 8 characters, thank you so much"
        if postData["password"] != postData["confirm_password"]:
                errors[0]["password_confirm"] = "» Hey your password and confirm password have to match, thank you so much"
        if len(errors[0]) < 1:
            errors[1] = User.objects.create(email=postData["email"].upper(), password=bcrypt.hashpw(postData["password"].encode(), bcrypt.gensalt()).decode(), first_name=postData["first_name"], last_name=postData["last_name"], username=postData["username"]).id
        return errors

    def login_validator(self, postData):
        errors = [{}, None]
        if postData["username"] == "":
            errors[0]["username"] = "» Username cannot be empty"
        else:
            errors[1] = 1
            if len(User.objects.filter(username=postData["username"])) == 0:
                errors[0]["username"] = "» Username does not exist"
            else:
                user = User.objects.get(username=postData["username"])
                if not bcrypt.checkpw(postData["password"].encode(), user.password.encode()):
                    errors[0]["password"] = "» That's incorrect"
                else:
                    errors[1] = user.id
        return errors

class TripManager(models.Manager):
    def trip_validator(self, postData):
        errors = {}
        if len(postData["destination"]) < 1:
            errors["destination"] = "» Your destination cannot be nowhere"
        if len(postData["description"]) < 1:
            errors["description"] = "» Your description cannot be nothing"
        if not postData["travel_start"]:
            errors["travel_start"] = "» You need a start date, thank you so much"
        if not postData["travel_end"]:
            errors["travel_end"] = "» You need an end date, thank you so much"
        if postData["travel_start"] and postData["travel_end"]:
            if postData["travel_end"] < postData["travel_start"]:
                errors["invalid1"] = "» This does not make sense... try again, thank you so much"
            if datetime.now() > datetime.strptime(postData["travel_start"], "%Y-%m-%d"):
                errors["invalid2"] = "» You cannot start your trip in the past, or today"
        print(errors)
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    def __repr__(self):
        return f"<User object: {self.first_name} {self.last_name} ({self.id})>"

class Trip(models.Model):
    destination = models.CharField(max_length=255)
    description = models.TextField()
    travel_start = models.DateTimeField()
    travel_end = models.DateTimeField()
    user_planner = models.ForeignKey(User, related_name="planned_trips", on_delete=models.CASCADE)
    user_joined = models.ManyToManyField(User, related_name="joined_trips")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TripManager()
    def __repr__(self):
        return f"<Trip object: {self.destination} ({self.id})>"