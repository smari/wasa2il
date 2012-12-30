#coding:utf-8

from datetime import datetime, timedelta
import logging

from django.db import models
from django.contrib.auth.models import User

#from fields import CreatedField, ModifiedField, AutoUserField
from base_classes import NameSlugBase, getCreationBase
from django.utils.translation import ugettext as _


nullblank = {'null': True, 'blank': True}


class BaseIssue(NameSlugBase):
	description		= models.TextField(**nullblank)


class UserProfile(models.Model):
	"""A user's profile data. Contains various informative areas, plus various settings."""
	user			= models.OneToOneField(User)


	# User information
	displayname		= models.CharField(max_length="255", verbose_name="Display name", help_text="The name to display on the site.", **nullblank)
	email_visible		= models.BooleanField(default=False, help_text="Whether to display your email address on your profile page.")
	bio			= models.TextField(**nullblank)
	picture			= models.ImageField(upload_to="users", **nullblank)

	# User settings
	language		= models.CharField(max_length="6", default="en")
	topics_showall		= models.BooleanField(default=True, help_text="Whether to show all topics in a polity, or only starred.")


	def __unicode__(self):
		return 'Profile for %s (%d)' % (unicode(self.user), self.user.id)


class PolityRuleset(models.Model):
	"""A polity's ruleset."""
	polity			= models.ForeignKey('Polity')
	name			= models.CharField(max_length=255)

	# Issue quora is how many members need to support a discussion
	# before it goes into proposal mode. If 0, use timer.
	# If issue_quora_percent, user percentage of polity members.
	issue_quora_percent	= models.BooleanField()
	issue_quora		= models.IntegerField()

	# Issue majority is how many percent of the polity are needed
	# for a decision to be made on the issue.
	issue_majority		= models.IntegerField()

	# Denotes how many seconds an issue is in various phases.
	issue_discussion_time	= models.IntegerField()
	issue_proposal_time	= models.IntegerField()
	issue_vote_time		= models.IntegerField()

	# Sometimes we require an issue to be confirmed with a secondary vote.
	# Note that one option here is to reference the same ruleset, and thereby
	# force continuous confirmation (such as with annual budgets, etc..)
	# Also, can be used to create multiple discussion rounds
	confirm_with		= models.ForeignKey('PolityRuleset', **nullblank)

	# For multi-round discussions, we may want corresponding documents not to
	# be adopted when the vote is complete, but only for the successful vote
	# to allow progression into the next round.
	adopted_if_accepted	= models.BooleanField()


	def has_quora(self, issue):
		# TODO: Return whether this has acheived quora on this ruleset
		pass

	def has_majority(self, issue):
		# TODO: Return whether this has majority on this ruleset
		pass

	def get_phase(self, issue):
		# TODO: Return information about the current phase
		pass

	def get_timeline(self, issue):
		# TODO: Return a data structure describing when things will happen
		# Should contain reference to confirmation actions, but not expand
		# on them (as this could be an infinite loop, and confirmation 
		# actions aren't actually determined until post-vote.
		pass


class Polity(BaseIssue, getCreationBase('polity')):
	"""A political entity. See the manual."""

	parent			= models.ForeignKey('Polity', help_text="Parent polity", **nullblank)
	members			= models.ManyToManyField(User)
	invite_threshold	= models.IntegerField(default=3, help_text="How many members need to vouch for a new member before he can join.")

	is_listed		= models.BooleanField("Publicly listed?", default=True, help_text="Whether this polity is publicly listed or not.")
	is_nonmembers_readable	= models.BooleanField("Publicly viewable?", default=True, help_text="Whether non-members can view the polity and its activities.")

	image			= models.ImageField(upload_to="polities", **nullblank)

	document_frontmatter	= models.TextField(**nullblank)
	document_midmatter	= models.TextField(**nullblank)
	document_footer		= models.TextField(**nullblank)

	def get_delegation(self, user):
		"""Check if there is a delegation on this polity."""
		try:
			d = Delegate.objects.get(user=user, base_issue=self)
			return d.get_path()
		except:
			pass
		return []


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
	"""A collection of issues unified categorically."""
	polity			= models.ForeignKey(Polity)
	image			= models.ImageField(upload_to="polities", **nullblank)

	class Meta:
		ordering	= ["name"]


	def get_delegation(self, user):
		"""Check if there is a delegation on this topic."""
		try:
			d = Delegate.objects.get(user=user, base_issue=self)
			return d.get_path()
		except:
			return self.polity.get_delegation(user)

	def new_comments(self):
		return Comment.objects.filter(issue__topics=self).order_by("-created")[:10]


class UserTopic(models.Model):
	"""Whether a user likes a topic."""
	topic			= models.ForeignKey(Topic)
	user			= models.ForeignKey(User)

	class Meta:
		unique_together	= (("topic", "user"),)


class Issue(BaseIssue, getCreationBase('issue')):
	polity 			= models.ForeignKey(Polity)
	topics			= models.ManyToManyField(Topic)
	options			= models.ManyToManyField('VoteOption')
	deadline_proposals	= models.DateTimeField()
	deadline_votes		= models.DateTimeField()
	ruleset			= models.ForeignKey(PolityRuleset)

	def __unicode__(self):
		return self.name

	def get_delegation(self, user):
		"""Check if there is a delegation on this topic."""
		try:
			d = Delegate.objects.get(user=user, base_issue=self)
			return d.get_path()
		except:
			for i in self.topics.all():
				return i.get_delegation(user)

	def topics_str(self):
		return ', '.join(map(str, self.topics.all()))

	def proposed_documents(self):
		return self.document_set.filter(is_proposed=True)

	def user_documents(self, user):
		return self.document_set.filter(is_proposed=False, user=user)


class Comment(getCreationBase('comment')):
	comment			= models.TextField()
	issue			= models.ForeignKey(Issue)


class Delegate(models.Model):
	polity			= models.ForeignKey(Polity)
	user			= models.ForeignKey(User)
	delegate		= models.ForeignKey(User, related_name='delegate_user')
	base_issue		= models.ForeignKey(BaseIssue)

	class Meta:
		unique_together = (('user', 'base_issue'))

	def __unicode__(self):
		return "[%s:%s] %s -> %s" % (self.type(), self.base_issue, self.user, self.delegate)

	def polity(self):
		"""Gets the polity that the delegation exists within."""
		try: return self.base_issue.issue.polity
		except: pass
		try: return self.base_issue.topic.polity
		except: pass
		try: return self.base_issue.polity
		except: pass

	def result(self):
		"""Work through the delegations and figure out where it ends"""
		print self.get_path()
		return self.get_path()[-1].delegate

	def type(self):
		"""Figure out what kind of thing is being delegated. Returns a translated string."""
		try:
			b = self.base_issue.issue
			return _("Issue")
		except: pass
		try:
			b = self.base_issue.topic
			return _("Topic")
		except: pass
		try:
			b = self.base_issue.polity
			return _("Polity")
		except: pass

	def get_power(self):
		"""Get how much power has been transferred through to this point in the (reverse) delegation chain."""
		# TODO: FIXME
		pass


	def get_path(self):
		"""Get the delegation pathway from here to the end of the chain."""
		path = [self]
		while True:
			item = path[-1]
			user = item.delegate
			dels = user.delegate_set.filter(base_issue=item.base_issue)
			if len(dels) > 0:
				path.append(dels[0])
				continue

			try: # If this works, we are working with an "Issue"
				base_issue = item.base_issue.issue
				for topic in base_issue.topics.all():
					dels = user.delegate_set.filter(base_issue=topic)
					if len(dels) > 0:
						# TODO: FIXME
						# Problem: Whereas an issue can belong to multiple topics, this is
						#  basically picking the first delegation to a topic, rather than
						#  creating weightings. Should we do weightings?
						path.append(dels[0])
						continue
			except: pass
			
			try: # If this works, we are working with an "Issue"
				base_issue = item.base_issue.topic
				dels = user.delegate_set.filter(base_issue=base_issue)
				if len(dels) > 0:
					path.append(dels[0])
					continue
			except: pass
			
			break

		return path



class VoteOption(NameSlugBase):
	pass


class Vote(models.Model):
	user			= models.ForeignKey(User)
	issue			= models.ForeignKey(Issue)
	option			= models.ForeignKey(VoteOption)
	cast			= models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = (('user', 'issue'))

	def power(self):
		# Follow reverse delgation chain to discover how much power we have.
		p = 1

		return p


class MembershipVote(models.Model):
	voter			= models.ForeignKey(User, related_name="membership_granter")
	user			= models.ForeignKey(User, related_name="membership_seeker")
	polity			= models.ForeignKey(Polity)

	def save(self, *args, **kwargs):
		super(MembershipVote, self).save(*args, **kwargs)
		try:
			m = MembershipRequest.objects.get(requestor=self.user, polity=self.polity)
			if m.get_fulfilled() and m.left == False:
				logging.debug('fulfilled!')
				self.polity.members.add(self.user)
		except MembershipRequest.DoesNotExist:
			logging.error('MembershipRequest object not found for requestor %s (id:%d) and polity %s (id:%d)' % (self.requestor, self.requestor.id, self.polity, self.polity.id))

	def __repr__(self):
		return 'Vote: %s for %s' % (repr(self.voter), repr(self.user))

	class Meta:
		unique_together = (("voter", "user", "polity"),)


class MembershipRequest(models.Model):
	requestor		= models.ForeignKey(User)
	polity			= models.ForeignKey(Polity)
	fulfilled		= models.BooleanField(default=False)
	fulfilled_timestamp	= models.DateTimeField(null=True)
	left			= models.BooleanField(default=False)

	class Meta:
		unique_together = (("requestor", "polity"),)

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
		return self.statement_set.filter(type__in=[2, 3])

	def support(self):
		# % of support for the document in its polity.
		return 100

	def get_contributors(self):
		return set([x.user for x in self.statement_set.all()])


class Statement(models.Model):
	user			= models.ForeignKey(User)
	document		= models.ForeignKey(Document)
	type			= models.IntegerField()
	number			= models.IntegerField()

	def __unicode__(self):
		try:
			return self.statementoption_set.filter(user=self.user)[0].text
		except:
			return ""

	def get_options(self):
		return self.statementoption_set.all()

	def get_options_count(self):
		return self.statementoption_set.count()



class StatementOption(models.Model):
	statement 		= models.ForeignKey(Statement)
	user			= models.ForeignKey(User)
	text			= models.TextField()

	def __unicode__(self):
		return self.text


class ChangeProposal(models.Model):
	document 		= models.ForeignKey(Document)	# Document to reference
	user 			= models.ForeignKey(User)		# Who proposed it
	timestamp 		= models.DateTimeField(auto_now_add=True)	# When
	actiontype		= models.IntegerField()			# Type of change to make [all]
	refitem			= models.IntegerField()			# Number what in the sequence to act on [all]
	destination		= models.IntegerField()			# Destination of moved item, or of new item [move, add]
	content			= models.TextField()			# Content for new item, or for changed item (blank=same on change) [change, add]
	contenttype		= models.IntegerField()			# Type for new content, or of changed item (0=same on change) [change, add]

	# == Examples ==
	#	ChangeProposal(actiontype=1, refitem=2)                                         # Delete item 2 from the proposal
	#	ChangeProposal(actiontype=2, refitem=2, destination=3)                          # Move item 2 to after item 3 (Bar after Baz)
	#	ChangeProposal(actiontype=2, refitem=2, destination=0)                          # Move item 2 to after item 0 (beginning of list)
	#	ChangeProposal(actiontype=3, refitem=2, content="Splurg")                       # Change text of item 2 from "Bar" to "Splurg"
	#	ChangeProposal(actiontype=4, refitem=2, content="Splurg", contenttype=2)        # Add "statement" object containing "Splurg" after "Bar"
	#


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
	attendees		= models.ManyToManyField(User, related_name="attendees", **nullblank)

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

	def __unicode__(self):
		ret = 'Meeting %sat %s' % (('at %s' % self.location) if self.location else '', self.time_starts)
		if self.ended():
			ret += ' (finished)'
		return ret


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
	done			= models.IntegerField()	 # 0 = Not done, 1 = Active, 2 = Done

	def __unicode__(self):
		return self.item


class MeetingIntervention(models.Model):
	meeting			= models.ForeignKey(Meeting)
	user			= models.ForeignKey(User)
	agendaitem		= models.ForeignKey(MeetingAgenda)
	motion			= models.IntegerField()
	order			= models.IntegerField()
	done			= models.IntegerField()	 # 0 = Not done, 1 = Active, 2 = Done

	def __unicode__(self):
		return self.user.username
