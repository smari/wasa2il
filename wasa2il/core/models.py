from django.db import models

from django.contrib.auth.models import User

from fields import NameField, NameSlugField, CreatedField, ModifiedField, AutoUserField
from base_classes import getCreationBase

nullblank = { 'null': True, 'blank': True }



class BaseIssue(models.Model):
	name			= NameField()
	slug			= NameSlugField()
	description		= models.TextField(**nullblank)

class Polity(BaseIssue, getCreationBase('polity')):
	parent			= models.ForeignKey('Polity', **nullblank)
	invite_threshold	= models.IntegerField(default=3)


class Topic(BaseIssue, getCreationBase('topic')):
	polity			= models.ForeignKey(Polity)

class Issue(BaseIssue, getCreationBase('issue')):
	topic			= models.ManyToManyField(Topic)

class Comment(getCreationBase('comment')):
	comment			= models.TextField()
	issue			= models.ForeignKey(Issue)

class Delegate(models.Model):
	user			= models.ForeignKey(User)
	delegate		= models.ForeignKey(User, related_name='delegate_user')
	base_issue		= models.ForeignKey(BaseIssue)
