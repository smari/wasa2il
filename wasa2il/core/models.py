#coding:utf-8

from datetime import datetime, timedelta
import logging

from django.db import models
from django.contrib.auth.models import User

#from fields import CreatedField, ModifiedField, AutoUserField
from base_classes import NameSlugBase, getCreationBase


nullblank = {'null': True, 'blank': True}

class BaseIssue(NameSlugBase):
	description		= models.TextField(**nullblank)


class UserProfile(models.Model):
	user			= models.ForeignKey(User)
	bio			= models.TextField(**nullblank)
	picture			= models.ImageField(upload_to="users", **nullblank)

	topics_showall		= models.BooleanField(default=True, help_text="Whether to show all topics in a polity, or only starred.")

	def __unicode__(self):
		return 'Profile for %s (%d)' % (unicode(self.user), self.user.id)


class Polity(BaseIssue, getCreationBase('polity')):
	parent			= models.ForeignKey('Polity', help_text="Parent polity",**nullblank)
	members			= models.ManyToManyField(User)
	invite_threshold	= models.IntegerField(default=3, help_text="How many members need to vouch for a new member before he can join.")

	is_listed		= models.BooleanField("Publicly listed?", default=True, help_text="Whether this polity is publicly listed or not.")
	is_nonmembers_readable	= models.BooleanField("Publicly viewable?", default=True, help_text="Whether non-members can view the polity and its activities.")

	image			= models.ImageField(upload_to="polities", **nullblank)

	def is_member(self, user):
		return user in self.members.all()

	def get_invite_threshold(self):
		return min(self.members.count(), self.invite_threshold)

	def get_topic_list(self, user):
		if user.get_profile().topics_showall:
			topics = Topic.objects.filter(polity=self)
		else:
			topics = [x.topic for x in UserTopic.objects.filter(user=user, topic__polity=self)]

		return topics


	def meetings_upcoming(self):
		return self.meeting_set.filter(time_started=None)

	def meetings_ongoing(self):
		return self.meeting_set.filter(time_started__gt=datetime.now(), time_ended=None)

	def meetings_ended(self):
		return self.meeting_set.filter(time_ended__gt=datetime.now())

	def agreements(self):
		return self.document_set.filter(is_adopted=True)


class Topic(BaseIssue, getCreationBase('topic')):
	polity			= models.ForeignKey(Polity)
	image			= models.ImageField(upload_to="polities", **nullblank)

	class Meta:
		ordering	= ["name"]

	def new_comments(self):
		return Comment.objects.filter(issue__topics=self).order_by("-created")[:10]


class UserTopic(models.Model):
	topic			= models.ForeignKey(Topic)
	user			= models.ForeignKey(User)

	class Meta:
		unique_together	= (("topic", "user"),)


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


class MembershipVote(models.Model):
	voter			= models.ForeignKey(User, related_name="membership_granter")
	user			= models.ForeignKey(User, related_name="membership_seeker")
	polity			= models.ForeignKey(Polity)

	def save(self, *args, **kwargs):
		super(MembershipVote, self).save(*args, **kwargs)
		try:
			m = MembershipRequest.objects.get(requestor=self.user, polity=self.polity)
			if m.get_fulfilled():
				logging.debug('fulfilled!')
				self.polity.members.add(self.user)
		except MembershipRequest.DoesNotExist:
			logging.error('MembershipRequest object not found for requestor %s (id:%d) and polity %s (id:%d)' % (self.requestor, self.requestor.id, self.polity, self.polity.id))

	def __repr__(self):
		return 'Vote: %s for %s' % (repr(self.voter), repr(self.user))

	class Meta:
		unique_together = ( ("voter", "user", "polity"), )


class MembershipRequest(models.Model):
	requestor		= models.ForeignKey(User)
	polity			= models.ForeignKey(Polity)
	fulfilled		= models.BooleanField(default=False)
	fulfilled_timestamp	= models.DateTimeField(null=True)

	class Meta:
		unique_together = ( ("requestor", "polity"), )

	def votes(self):
		return MembershipVote.objects.filter(user=self.requestor, polity=self.polity).count()

	def votesneeded(self):
		return self.polity.get_invite_threshold()

	def votespercent(self):
		pc = int(100 * (float(self.votes()) / self.votesneeded()))
		return min(max(pc, 0), 100)

	def get_fulfilled(self):
		# Recalculate at most once per hour.
		if self.fulfilled_timestamp == None or self.fulfilled_timestamp < datetime.now() - timedelta(seconds=3600):
			self.fulfilled = self.votes() >= self.votesneeded()
			self.save()

		return self.fulfilled

	def __unicode__(self):
		ret = u'Request: %s for %s' % (unicode(self.requestor), self.polity.name)
		if self.fulfilled:
			ret += ' (fulfilled)'
		return ret


class Document(NameSlugBase):
	polity			= models.ForeignKey(Polity)
	issues			= models.ManyToManyField(Issue)
	user			= models.ForeignKey(User)
	is_adopted		= models.BooleanField(default=False)
	is_proposed		= models.BooleanField(default=False)

	def __unicode__(self):
		return self.name

	def get_references(self):
		return self.statement_set.filter(type=0)

	def get_assumptions(self):
		return self.statement_set.filter(type=1)

	def get_declarations(self):
		return self.statement_set.filter(type__in=[2,3])

	def support(self):
		# % of support for the document in its polity.
		return 100


class Statement(models.Model):
	user			= models.ForeignKey(User)
	document		= models.ForeignKey(Document)
	type			= models.IntegerField()
	number			= models.IntegerField()
	text			= models.ManyToManyField('StatementOption')

	def __unicode__(self):
		print self.get_text()
		return self.get_text()


	def get_text(self, rev=0):
		try:
			text = self.text.all()[rev].text
		except:
			text = ""

		if self.type == 0:
			try:
				doc = Document.objects.get(id=text)
				# FIXME: BLERGH!!!!
				return u"Með tilvísun í <a href=\"/polity/%d/document/%d/\">%s</a>" % (doc.polity.id, doc.id, doc.name)
			except Exception, e:
				print e
				# FIXME: BLERGH!!!!
				return u"Með tilvísun í óþekkt skjal."
		else:
			return text

class StatementOption(models.Model):
	user			= models.ForeignKey(User)
	text			= models.TextField()

	
class Meeting(models.Model):
	class Meta:
		ordering	= ["time_starts", "time_ends"]

	user			= models.ForeignKey(User, related_name="created_by")
	polity			= models.ForeignKey(Polity)
	location		= models.CharField(max_length=200, **nullblank)
	time_starts		= models.DateTimeField(blank=True, null=True)
	time_started		= models.DateTimeField(blank=True, null=True)
	time_ends		= models.DateTimeField(blank=True, null=True)
	time_ended		= models.DateTimeField(blank=True, null=True)
	is_agenda_open		= models.BooleanField(default=True)
	managers		= models.ManyToManyField(User, related_name="managers")
	attendees		= models.ManyToManyField(User, related_name="attendees")

	def get_status(self):
		if self.notstarted():
			return "Not started"

		if self.ongoing():
			return "Ongoing"

		if self.ended():
			return "Ended"

	def notstarted(self):
		if not self.time_started:
			return True
		return False

	def ongoing(self):
		if not self.time_started:
			return False

		if not self.time_ended:
			return True

		if datetime.now() > self.time_started and (not self.time_ended or datetime.now() < self.time_ended):
			return True

		return False

	def ended(self):
		if not self.time_ended:
			return False

		if datetime.now() > self.time_ended:
			return True
		return False


class MeetingRules(models.Model):
	length_intervention		= models.IntegerField(default=300, help_text="The maximum length of an intervention.")
	length_directresponse	= models.IntegerField(default=60, help_text="The maximum length of a direct response.")
	length_clarify			= models.IntegerField(default=30, help_text="The maximum length of a clarification.")
	length_pointoforder		= models.IntegerField(default=60, help_text="The maximum length of a point of order.")
	max_interventions		= models.IntegerField(default=0, help_text="The maximum number of interventions a user can make in one topic. 0 = unlimited.")
	max_directresponses		= models.IntegerField(default=0, help_text="The maximum number of direct responses a user can make in one topic. 0 = unlimited.")
	max_clarify				= models.IntegerField(default=0, help_text="The maximum number of clarifications a user can make in one topic. 0 = unlimited.")
	max_pointoforder		= models.IntegerField(default=0, help_text="The maximum number of points of order a user can make in one topic. 0 = unlimited.")


class MeetingAgenda(models.Model):
	meeting			= models.ForeignKey(Meeting)
	item			= models.CharField(max_length=200)
	order			= models.IntegerField()
	done			= models.IntegerField()	# 0 = Not done, 1 = Active, 2 = Done

	def __unicode__(self):
		return self.item


class MeetingIntervention(models.Model):
	meeting			= models.ForeignKey(Meeting)
	user			= models.ForeignKey(User)
	agendaitem		= models.ForeignKey(MeetingAgenda)
	motion			= models.IntegerField()
	order			= models.IntegerField()
	done			= models.IntegerField()	# 0 = Not done, 1 = Active, 2 = Done

	def __unicode__(self):
		return user.username

