from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseNotFound
from django.db import connection
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
import datetime
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

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    with connection.cursor() as cursor:
        rv = cursor.execute('select user_id from user where username = ?',
                        [username]).fetchone()
    return rv[0] if rv else None

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
    
    followers = models.Follower.objects.filter(who_id=request.user.id).values()

    # Add the messages of followed users
    for follower in followers:
        follower_messages = unflagged.filter(user__id=follower.whom_id).values()
        messages.extend(follower_messages)
    
    # Add the messages of the user
    print(messages)
    user_messages = unflagged.filter(user__id=request.user.id).values()
    messages.extend(user_messages)

    context = {
        'messages': messages,
    }
    return render(request, '../templates/timeline.html', context)


def public_timeline(request):
    """Displays the latest messages of all users."""
    # Fetch all messages
    messages = models.Message.objects.filter(flagged=0).order_by('-pub_date').values()
    # Convert to list of dicts
    print(messages,'hi')

    messages = [ dict(message) for message in list(messages) ]
    
    # Add user info to each message

    for message in messages:
        message["username"] = User.objects.get(id=message['user_id'])
    

    context = {
        'messages': messages,
    }
    return render(request, '../templates/timeline.html', context)


def user_timeline(request, username):
    try:
        #We do we not use filter
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound("Username does not exist")

    # Check following
    try:
        models.Follower.objects.filter(who_id=request.user.id, whom_id=user.id).get()
        followed = True
    except:
        followed = False

    # Fetch all messages
    messages = models.Message.objects.filter(user__id=user.id).order_by('-pub_date').values()

    # Convert to list of dicts
    messages = [ dict(message) for message in messages ]
    # print(messages)
    # Add user info to each message
    
    for message in messages:
        message["username"] = User.objects.get(id=message['user_id'])
    
    print(messages)
    context = {
        'messages': messages,
        'followed': followed,
        'profile_user': user,
    }
    return render(request, '../templates/timeline.html', context)

# /follow
def follow_user(request, username):
    """Adds the current user as follower of the given user."""
    
    if not request.user:
        return redirect('public/')

    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound("Username does not exist")

    try:
        follow = models.Follower.objects.filter(who_id=request.user, whom_id=user).get()
        followed = True
    except:
        followed = False

    if followed:
        follow.delete()
    else:
        models.Follower.objects.create(who_id=request.user, whom_id=user)

    return redirect('user_timeline', username=username)
    # if user exists, do stuff
    # if models.User.object.get(username=username).exists():


    # else:
        # HttpResponseNotFound("User does not exist...")

    # whom_id = models.User

    # #whom_id = get_user_id(username)
    # if whom_id is None:
    #     HttpResponseNotFound("User does not exist...")
    # with connection.cursor() as cursor:
    #     cursor.execute('insert into follower (who_id, whom_id) values (?, ?)',
    #                 [session['user_id'], whom_id]) # missing session?
    #     cursor.commit()
    # # flash(f'You are now following "{username}") # need flash equivalent
    # return #redirect('timeline')


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


def add_message(request):
    """Registers a new message for the user."""
    if request.user.is_authenticated:
        message_object = models.Message.objects.create(
            user = request.user,
            text = request.POST['text'],
            flagged = 0
        ) 
        
        message_object.save()

        #g.db.execute('''insert into message (author_id, text, pub_date, flagged)
        #    values (?, ?, ?, 0)''', (session['user_id'], request.form['text'],
        #                          int(time.time())))
        #g.db.commit()
        #flash('Your message was recorded')
    else:
        return HttpResponseNotFound("User not logged in")
    return redirect('public')
