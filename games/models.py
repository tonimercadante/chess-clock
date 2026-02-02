from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

Users = get_user_model()


# Create your models here.
class Clocks(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    description = models.TextField()
    start_time = models.IntegerField()
    incremental_time = models.IntegerField()


class Games(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    player_white = models.ForeignKey(Users, related_name='white_games', on_delete=models.PROTECT)
    player_black = models.ForeignKey(Users, related_name='black_games', on_delete=models.PROTECT)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    clock = models.ForeignKey(Clocks, on_delete=models.PROTECT)


class Moves(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField()
    game = models.ForeignKey(Games, on_delete=models.PROTECT)
