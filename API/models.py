from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Room(models.Model):
    room_id = models.CharField(max_length=6)
    members = models.ManyToManyField(to=User,related_name="game_members")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_owner")

    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="game_winner")

    game_started = models.BooleanField(default=False)

    match_ended  = models.BooleanField(default=False)

    def __str__(self):
        return self.room_id

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message({self.user} {self.room})"


class Leaderboard(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="leaderboards")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(0)
    won = models.BooleanField(default=False)
    time = models.IntegerField(default=0)


class RoomScores(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    life = models.IntegerField(default=3)
    game_over = models.BooleanField(default=False)

    def __str__(self):
        return self.room.room_id + " " + self.user.first_name
    
