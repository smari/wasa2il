#!/usr/bin/env python

import sys
from core.models import *
from django.contrib.auth.hashers import *

users = User.objects.all()
for user in users:
	guess = user.username[::-1]
	if check_password(guess, user.password):
		print "%s (%s, %s)" % (user.get_name(), user.username, user.email)

