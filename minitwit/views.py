from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseNotFound
from django.db import connection
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User

from . import models

import time
import sqlite3
from hashlib import md5
from datetime import datetime
from contextlib import closing


#### Helper functions

PER_PAGE = 30


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    with connection.cursor() as cursor:
        cursor.execute(query, args)
        rv = [dict((cursor.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cursor.fetchall()]
    return (rv[0] if rv else None) if one else rv


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)



### Views
# /, /public
def timeline(request):
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    print(("We got a visitor from: " + str(request)))
    if not request.user:
        return redirect('public/')
    
    messages = []
    unflagged = models.Message.objects.filter(flagged=0)
    
    followers = models.Follower.objects.filter(who_id=request.user.id)

    # Add the messages of followed users
    for follower in followers:
        follower_messages = unflagged.filter(author_id=follower.whom_id)
        messages.extend(follower_messages)
    
    # Add the messages of the user
    user_messages = unflagged.filter(author_id=request.user.id)
    messages.extend(user_messages)

    context = {
        'messages': messages,
    }
    return render(request, '../templates/timeline.html', context)


def public_timeline(request):
    """Displays the latest messages of all users."""
    # Fetch all messages
    messages = models.Message.objects.filter(flagged=0)

    # Convert to list of dicts
    messages = [ dict(message) for message in messages ]

    # Add user info to each message
    messages = [
        message.update(
            models.User.objects.filter(user_id=message.author_id).get(),
        )
        for message in messages
    ]
    context = {
        'messages': messages,
    }
    return render(request, '../templates/timeline.html', context)


def user_timeline(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound("Username does not exist")
    
    print(user)
    # Check following
    try:
        models.Follower.objects.filter(who_id=request.user.id, whom_id=user.id).get()
        followed = True
    except:
        followed = False

    # Fetch all messages
    messages = models.Message.objects.filter(author_id=user.id)

    # Convert to list of dicts
    messages = [ dict(message) for message in messages ]

    # Add user info to each message
    messages = [
        message.update(
            models.User.objects.filter(user_id=message.author_id).get(),
        )
        for message in messages
    ]
    context = {
        'messages': messages,
        'followed': followed,
        'profile_user': user,
    }
    return render(request, '../templates/timeline.html', context)




# /login
def login(request):
    """ Login """
    if request.method == "POST":
        user = authenticate(username = request.POST['username'], password = request.POST['password'])
        if user is None:
            return HttpResponseNotFound("Wrong credentials")
        else:
            auth_login(request, user)
            return redirect('/public')
    return render(request, '../templates/login.html', {})

# /register
def register(request):
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    error = None
    if request.method == "POST":
        if request.POST['password'] != request.POST['password2']:
            error = 'The passwords do not match'
        else:
            # TODO: Write better secuirty measures skrrrrt

            user = User.objects.create_user(
                request.POST['username'],
                request.POST['email'],
                request.POST['password']
            )
            
            user.save()
            return redirect('login')
    return render(request, '../templates/register.html', {'error': error})

# /logout
def logout(request):
    """ Logout """
    auth_logout(request)
    return redirect('public')

