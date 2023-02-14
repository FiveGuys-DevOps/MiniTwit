from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=30, unique=True)
    pw_hash = models.CharField(max_length=100)

class Follower(models.Model):
    who_id = models.IntegerField()
    whom_id = models.IntegerField()


class Message(models.Model):
    text = models.TextField()
    pub_date = models.IntegerField()
    author_id = models.IntegerField()
    flagged = models.IntegerField()
    