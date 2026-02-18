from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.
class Users(AbstractUser):
    pass

class Types(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.TextField()

    def __str__(self):
        return self.name

class Ratings(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    type = models.ForeignKey(Types, on_delete=models.PROTECT) 
    rating = models.IntegerField(default=0)


class Clocks(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    description = models.TextField()
    start_time = models.IntegerField()
    incremental_time = models.IntegerField()
    type = models.ForeignKey(Types, on_delete=models.PROTECT) 


class Games(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    player_white = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='white_games', on_delete=models.PROTECT)
    player_black = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='black_games', on_delete=models.PROTECT)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    clock = models.ForeignKey(Clocks, on_delete=models.PROTECT)


class Moves(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField()
    game = models.ForeignKey(Games, on_delete=models.PROTECT)
