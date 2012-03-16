from django.db import models

from django.contrib.auth.models import User

from fields import NameField, NameSlugField, CreatedField, ModifiedField, AutoUserField
from base_classes import getCreationBase

nullblank = { 'null': True, 'blank': True }



class BaseIssue(models.Model):
	name			= NameField()
	slug			= NameSlugField()
	description		= models.TextField(**nullblank)
	def __unicode__(self):
		return u'%s' % (self.name)

class Polity(BaseIssue, getCreationBase('polity')):
	parent			= models.ForeignKey('Polity', **nullblank)
	members			= models.ManyToManyField(User)
	invite_threshold	= models.IntegerField(default=3)

	is_listed		= models.BooleanField(default=True)
	is_nonmembers_readable	= models.BooleanField(default=True)

	def is_member(user):
		return user in self.members


class Topic(BaseIssue, getCreationBase('topic')):
	polity			= models.ForeignKey(Polity)

class Issue(BaseIssue, getCreationBase('issue')):
	topics			= models.ManyToManyField(Topic)
	def topics_str(self):
		return ', '.join(map(str, self.topics.all()))

class Comment(getCreationBase('comment')):
	comment			= models.TextField()
	issue			= models.ForeignKey(Issue)

class Delegate(models.Model):
	user			= models.ForeignKey(User)
	delegate		= models.ForeignKey(User, related_name='delegate_user')
	base_issue		= models.ForeignKey(BaseIssue)
