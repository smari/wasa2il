from datetime import datetime, timedelta
import logging

from django.db import models
from django.contrib.auth.models import User

from core.base_classes import NameSlugBase, getCreationBase
from django.utils.translation import ugettext as _

from core.models import *

nullblank = {'null': True, 'blank': True}


class Forum(models.Model):
	polity		= models.ForeignKey(Polity)
	name		= models.CharField(max_length=200)
	nonmembers_post	= models.BooleanField(default=False)


class Discussion(models.Model):
	forum		= models.ForeignKey(Forum)
	name		= models.CharField(max_length=200)
	started_by	= models.ForeignKey(User)


class DiscussionPost(models.Model):
	user		= models.ForeignKey(User)
	discussion	= models.ForeignKey(Discussion)
	text		= models.TextField()
	timestamp	= models.DateTimeField(auto_now_add=True)
	users_seen	= models.ManyToManyField(User, related_name="seen")
