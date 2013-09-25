#!/usr/bin/env python

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

users = User.objects.all()
for user in users:
    guess = user.username[::-1]
    if check_password(guess, user.password):
        print "%s (%s, %s)" % (user.get_name(), user.username, user.email)
