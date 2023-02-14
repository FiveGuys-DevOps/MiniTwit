from django.db import models


class Follower(models.Model):
    who_id = models.IntegerField()
    whom_id = models.IntegerField()


class Message(models.Model):
    text = models.TextField()
    pub_date = models.IntegerField()
    author_id = models.IntegerField()
    flagged = models.IntegerField()
    