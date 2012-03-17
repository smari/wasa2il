from django.db import models

from django.contrib.auth.models import User

#from fields import CreatedField, ModifiedField, AutoUserField
from base_classes import NameSlugBase, getCreationBase

nullblank = { 'null': True, 'blank': True }



class BaseIssue(NameSlugBase):
	description		= models.TextField(**nullblank)

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
	options			= models.ManyToManyField('VoteOption')

	def topics_str(self):
		return ', '.join(map(str, self.topics.all()))

	def polity(self):
		try:
			return self.topics.all()[0].polity
		except:
			return None

class Comment(getCreationBase('comment')):
	comment			= models.TextField()
	issue			= models.ForeignKey(Issue)

class Delegate(models.Model):
	user			= models.ForeignKey(User)
	delegate		= models.ForeignKey(User, related_name='delegate_user')
	base_issue		= models.ForeignKey(BaseIssue)
	class Meta:
		unique_together = (('user', 'base_issue'))

class VoteOption(NameSlugBase):
	pass

class Vote(models.Model):
	user			= models.ForeignKey(User)
	issue			= models.ForeignKey(Issue)
	option			= models.ForeignKey(VoteOption)
	cast			= models.DateTimeField(auto_now_add=True)
	class Meta:
		unique_together = (('user', 'issue'))


class MembershipRequest(models.Model):
	requestor		= models.ForeignKey(User)
	polity			= models.ForeignKey(Polity)

	class Meta:
		unique_together = ( ("requestor", "polity"), )

class MembershipVotes(models.Model):
	voter			= models.ForeignKey(User, related_name="membership_granter")
	user			= models.ForeignKey(User, related_name="membership_seeker")
