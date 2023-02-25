from django.db import models
from django.contrib.auth.models import User

#This is our database

class Follower(models.Model):
    who_id = models.IntegerField()
    whom_id = models.IntegerField()



class Message(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,default = 1,on_delete = models.CASCADE)
    flagged = models.IntegerField()

