from django.shortcuts import render

from django.db import connection

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

def timeline(request):
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    print(("We got a visitor from: " + str(request)))
    # if not g.user:
    #     return redirect(url_for('public_timeline'))
    
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

    print(request.user.id)

    print(messages)

    # Sort the messages by date
    # messages = messages.sort(key=lambda x: x.pub_date, reverse=True)[PER_PAGE:]

    # messages = query_db('''
    #     select message.*, user.* from message, user
    #     where message.flagged = 0 and message.author_id = user.user_id and (
    #         user.user_id = ? or
    #         user.user_id in (select whom_id from follower
    #                                 where who_id = ?))
    #     order by message.pub_date desc limit ?''',
    #     [request.user.id, request.user.id, PER_PAGE])

    context = {
        'messages': messages,
    }
    return render(request, '../templates/timeline.html', context)
