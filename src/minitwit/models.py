from django.contrib.auth.models import User
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

# This is our database


class Follower(ExportModelOperationsMixin("follower"), models.Model):
    who_id = models.ForeignKey(User, related_name="who", on_delete=models.CASCADE)
    whom_id = models.ForeignKey(User, related_name="whom", on_delete=models.CASCADE)


class Message(ExportModelOperationsMixin("message"), models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    flagged = models.IntegerField()
