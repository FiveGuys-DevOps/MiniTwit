from django.urls import path

from . import simviews

urls = [
    path("latest", simviews.latest, name="latest"),
    path("register", simviews.register, name="register"),
    path("msgs", simviews.all_msgs, name="msgs"),
    path("msgs/<str:username>", simviews.user_msgs, name="msgs_user"),
    path("fllws/<str:username>", simviews.follow_user, name="fllws_user"),
]
