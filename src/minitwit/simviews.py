from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from . import models

LATEST = 0

# Get latest
def latest(request):
    global LATEST
    return JsonResponse({"latest": int(LATEST)})

# Register user
@csrf_exempt
def register(request):
    username = json.loads(request.body)["username"]
    email = json.loads(request.body)["email"]
    pwd = json.loads(request.body)["pwd"]

    update_latest(request)
    error = None
    if request.method == "POST":
        if username == None:
            error = "You have to enter a username"
        elif email == None or "@" not in email:
            error = "You have to enter a valid email address"
        elif pwd == None:
            error = "You have to enter a password"
        else:
            try:
                User.objects.get(username=username)
                error = "The username is already taken"
            except:
                User.objects.create_user(
                    username,
                    email,
                    pwd
                )
    if error:
        return JsonResponse({'status': 400, 'error_msg': error}, status=400)

    return HttpResponse("", status=204)


# Get messages
@csrf_exempt
def all_msgs(request):
    update_latest(request)

    messages = models.Message.objects.all().order_by('-pub_date').values()
    messages = [ dict(message) for message in list(messages) ]

    amount = int(request.GET.get('no', 100))
    messages = messages[:amount]
    
    for message in messages:
        message['content'] = message['text']
        message['user'] = User.objects.get(id=message['user_id']).username

    return JsonResponse(messages, safe=False)


# Get user messages / Post message
@csrf_exempt
def user_msgs(request, username):
    update_latest(request)

    if request.method == "GET":
        user = User.objects.get(username=username)
        messages = models.Message.objects.filter(user=user).order_by('-pub_date').values()
        messages = [ dict(message) for message in list(messages) ]

        amount = int(request.GET.get('no', 100))
        messages = messages[:amount]

        print(messages)
        for message in messages:
            message['content'] = message['text']
            message['user'] = User.objects.get(id=message['user_id']).username

        return JsonResponse(messages, safe=False)

    elif request.method == "POST":

        try:
            user = User.objects.get(username=username)
        except:
            return JsonResponse({'status': 404, 'error_msg': "User not found"}, status=404) 
        message = models.Message.objects.create(
            text=json.loads(request.body)['content'],
            user=user,
            flagged=0
        )
    
    return HttpResponse(None, status=204)
    

# Follow/unfollow user
@csrf_exempt
def follow_user(request, username):
    update_latest(request)

    if request.method == "POST":
        user = User.objects.get(username=username)
        try:
            user_follow = json.loads(request.body)['follow']
            follower = User.objects.get(username=user_follow)
            models.Follower.objects.create(
                who_id=user,
                whom_id=follower
            )
        except:
            user_follow = json.loads(request.body)['unfollow']
            follower = User.objects.get(username=user_follow)
            try:
                models.Follower.objects.filter(
                    who_id=user,
                    whom_id=follower
                ).get().delete()
            except:
                logging.error("Followed user not found")
                return JsonResponse({'status': 404, 'error_msg': "Followed user not found"}, status=404)
    elif request.method == "GET":
        amount = int(request.GET.get('no', 100))
        user = User.objects.get(username=username)
        followers = models.Follower.objects.filter(who_id=user).values()
        followers = [ dict(follow) for follow in list(followers) ]
        followers = followers[:amount]

        followers_usernames = [
            User.objects.get(id=fo['whom_id_id']).username
            for fo in followers
        ]
        
        return JsonResponse({'follows': followers_usernames})
    return HttpResponse(None, status=204)




### Helper functions
def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    with connection.cursor() as cursor:
        cursor.execute(query, args)
        rv = [dict((cursor.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cursor.fetchall()]
    return (rv[0] if rv else None) if one else rv


def sim_middleware(request):
    from_simulator = request.headers.get("Authorization")
    if from_simulator != "Basic c2ltdWxhdG9yOnN1cGVyX3NhZmUh":
        error = "You are not authorized to use this resource!"
        return jsonify({"status": 403, "error_msg": error}), 403

# Update latest
def update_latest(request):
    global LATEST
    try_latest = request.GET['latest']
    LATEST = try_latest if try_latest != -1 else LATEST
    LATEST = int(LATEST)
