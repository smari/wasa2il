#coding:utf-8

import logging
import re
import random

from base_classes import NameSlugBase, getCreationBase
from core.utils import AttrDict
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from google_diff_match_patch.diff_match_patch import diff_match_patch

import schulze

nullblank = {'null': True, 'blank': True}


def trim(text, length):
    if len(text) > length:
        return '%s…' % text[:length - 1]
    return text


class BaseIssue(NameSlugBase):
    description = models.TextField(verbose_name=_("Description"), **nullblank)


class UserProfile(models.Model):
    """A user's profile data. Contains various informative areas, plus various settings."""
    user = models.OneToOneField(User)

    # Verification
    verified_ssn = models.CharField(max_length=30, null=True, blank=True, unique=True)
    verified_name = models.CharField(max_length=100, null=True, blank=True)
    verified_token = models.CharField(max_length=100, null=True, blank=True)
    verified_timing = models.DateTimeField(null=True, blank=True)

    # User information
    displayname = models.CharField(max_length="255", verbose_name=_("Name"), help_text=_("The name to display on the site."), **nullblank)
    email_visible = models.BooleanField(default=False, verbose_name=_("E-mail visible"), help_text=_("Whether to display your email address on your profile page."))
    bio = models.TextField(verbose_name=_("Bio"), **nullblank)
    picture = models.ImageField(upload_to="users", verbose_name=_("Picture"), **nullblank)
    joined_org = models.DateTimeField(null=True, blank=True) # Time when user joined organization, as opposed to registered in the system

    # User settings
    language = models.CharField(max_length="6", default="en", choices=settings.LANGUAGES, verbose_name=_("Language"))
    topics_showall = models.BooleanField(default=True, help_text=_("Whether to show all topics in a polity, or only starred."))

    def save(self, *largs, **kwargs):
        if not self.picture:
            self.picture.name = "default.jpg"
        super(UserProfile, self).save(*largs, **kwargs)

    def __unicode__(self):
        return 'Profile for %s (%d)' % (unicode(self.user), self.user.id)


def get_name(user):
    name = ""
    if user:
        try:
            name = user.userprofile.displayname
        except AttributeError:
            print 'User with id %d missing profile?' % user.id
            pass

    if not name:
        name = user.username

    return name

User.get_name = get_name


class PolityRuleset(models.Model):
    """A polity's ruleset."""
    polity = models.ForeignKey('Polity')
    name = models.CharField(max_length=255)

    # Issue quora is how many members need to support a discussion
    # before it goes into proposal mode. If 0, use timer.
    # If issue_quora_percent, user percentage of polity members.
    issue_quora_percent = models.BooleanField(default=False)
    issue_quora = models.IntegerField()

    # Issue majority is how many percent of the polity are needed
    # for a decision to be made on the issue.
    issue_majority = models.DecimalField(max_digits=5, decimal_places=2)

    # Denotes how many seconds an issue is in various phases.
    issue_discussion_time = models.IntegerField()
    issue_proposal_time = models.IntegerField()
    issue_vote_time = models.IntegerField()

    # Sometimes we require an issue to be confirmed with a secondary vote.
    # Note that one option here is to reference the same ruleset, and thereby
    # force continuous confirmation (such as with annual budgets, etc..)
    # Also, can be used to create multiple discussion rounds
    confirm_with = models.ForeignKey('PolityRuleset', **nullblank)

    # For multi-round discussions, we may want corresponding documents not to
    # be adopted when the vote is complete, but only for the successful vote
    # to allow progression into the next round.
    adopted_if_accepted = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

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

    parent = models.ForeignKey('Polity', help_text="Parent polity", **nullblank)
    members = models.ManyToManyField(User)
    officers = models.ManyToManyField(User, verbose_name=_("Officers"), related_name="officers")

    is_listed = models.BooleanField(verbose_name=_("Publicly listed?"), default=True, help_text=_("Whether the polity is publicly listed or not."))
    is_nonmembers_readable = models.BooleanField(verbose_name=_("Publicly viewable?"), default=True, help_text=_("Whether non-members can view the polity and its activities."))
    is_newissue_only_officers = models.BooleanField(verbose_name=_("Can only officers make new issues?"), default=False, help_text=_("If this is checked, only officers can create new issues. If it's unchecked, any member can start a new issue."))
    is_front_polity = models.BooleanField(verbose_name=_("Front polity?"), default=False, help_text=_("If checked, this polity will be displayed on the front page. The first created polity automatically becomes the front polity."))

    def get_delegation(self, user):
        """Check if there is a delegation on this polity."""
        if not user.is_authenticated():
            return []
        try:
            d = Delegate.objects.get(user=user, base_issue=self)
            return d.get_path()
        except Delegate.DoesNotExist:
            pass
        return []

    def is_member(self, user):
        return user in self.members.all()

    def get_topic_list(self, user):
        if user.is_anonymous() or UserProfile.objects.get(user=user).topics_showall:
            topics = Topic.objects.filter(polity=self).order_by('name')
        else:
            topics = [x.topic for x in UserTopic.objects.filter(user=user, topic__polity=self).order_by('topic__name')]

        return topics

    def agreements(self):
        return DocumentContent.objects.select_related('document').filter(status='accepted', document__polity_id=self.id).order_by('-issue__deadline_votes')

    def update_agreements(self):
        issues_to_process = Issue.objects.filter(is_processed=False).filter(deadline_votes__lt=timezone.now())
        for issue in issues_to_process:
            issue.process()
        return None

    def save(self, *args, **kwargs):

        polities = Polity.objects.all()
        if polities.count() == 0:
            self.is_front_polity = True
        elif self.is_front_polity:
            for frontpolity in polities.filter(is_front_polity=True).exclude(id=self.id): # Should never return more than 1
                frontpolity.is_front_polity = False
                frontpolity.save()

        return super(Polity, self).save(*args, **kwargs)


class Topic(BaseIssue, getCreationBase('topic')):
    """A collection of issues unified categorically."""
    polity = models.ForeignKey(Polity)

    class Meta:
        ordering = ["name"]

    def issues_open(self):
        issues = [issue for issue in self.issue_set.all() if issue.is_open()]
        return len(issues)

    def issues_voting(self):
        issues = [issue for issue in self.issue_set.all() if issue.is_voting()]
        return len(issues)

    def issues_closed(self):
        issues = [issue for issue in self.issue_set.all() if issue.is_closed()]
        return len(issues)

    def get_delegation(self, user):
        """Check if there is a delegation on this topic."""
        if not user.is_authenticated():
            return []
        try:
            d = Delegate.objects.get(user=user, base_issue=self)
            return d.get_path()
        except Delegate.DoesNotExist:
            return self.polity.get_delegation(user)

    def new_comments(self):
        return Comment.objects.filter(issue__topics=self).order_by("-created")[:10]


class UserTopic(models.Model):
    """Whether a user likes a topic."""
    topic = models.ForeignKey(Topic)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (("topic", "user"),)


class Issue(BaseIssue, getCreationBase('issue')):
    SPECIAL_PROCESS_CHOICES = (
        ('accepted_at_assembly', _('Accepted at assembly')),
        ('rejected_at_assembly', _('Rejected at assembly')),
    )

    polity = models.ForeignKey(Polity)
    topics = models.ManyToManyField(Topic, verbose_name=_("Topics"))
    documentcontent = models.OneToOneField('DocumentContent', related_name='issue', **nullblank)
    deadline_discussions = models.DateTimeField(**nullblank)
    deadline_proposals = models.DateTimeField(**nullblank)
    deadline_votes = models.DateTimeField(**nullblank)
    majority_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    ruleset = models.ForeignKey(PolityRuleset, verbose_name=_("Ruleset"), editable=True)
    is_processed = models.BooleanField(default=False)
    special_process = models.CharField(max_length='32', verbose_name=_("Special process"), choices=SPECIAL_PROCESS_CHOICES, default='', null=True, blank=True)

    class Meta:
        ordering = ["-deadline_votes"]

    def __unicode__(self):
        return self.name

    def apply_ruleset(self):
        now = datetime.now()

        if self.special_process:
            self.deadline_discussions = now
            self.deadline_proposals = now
            self.deadline_votes = now
        else:
            self.deadline_discussions = now + timedelta(seconds=self.ruleset.issue_discussion_time)
            self.deadline_proposals = self.deadline_discussions + timedelta(seconds=self.ruleset.issue_proposal_time)
            self.deadline_votes = self.deadline_proposals + timedelta(seconds=self.ruleset.issue_vote_time)

        self.majority_percentage = self.ruleset.issue_majority # Doesn't mechanically matter but should be official.

    def is_open(self):
        if not self.is_closed():
            return True
        return False

    def is_voting(self):
        if not self.deadline_proposals or not self.deadline_votes:
            return False

        if datetime.now() > self.deadline_proposals and datetime.now() < self.deadline_votes:
            return True

        return False

    def is_closed(self):
        if not self.deadline_votes:
            return False

        if datetime.now() > self.deadline_votes:
            return True

        return False

    def process(self):
        """
            Process issue
            - check if majority was reached
            - set document content to appropriate status
            - set issue status to processed
        """
        try:
            if self.majority_reached():
                #issue deadline has passed and majority achieved according to selected ruleset
                self.documentcontent.status = 'accepted'
            else:
                self.documentcontent.status = 'rejected'
            self.documentcontent.save()
            self.is_processed = True
            self.save()
            return True
        except Exception as e:
            return False


    def get_delegation(self, user):
        """Check if there is a delegation on this topic."""
        if not user.is_authenticated():
            return []
        try:
            d = Delegate.objects.get(user=user, base_issue=self)
            return d.get_path()
        except Delegate.DoesNotExist:
            for i in self.topics.all():
                return i.get_delegation(user)

    def topics_str(self):
        return ', '.join(map(str, self.topics.all()))

    def proposed_documents(self):
        return self.document_set.filter(is_proposed=True)

    def user_documents(self, user):
        try:
            return self.document_set.filter(user=user)
        except TypeError:
            return []

    def get_votes(self):
        votes = {}
        if self.is_closed():
            votes["yes"] = sum([x.get_value() for x in self.vote_set.filter(value=1)])
            votes["abstain"] = sum([x.get_value() for x in self.vote_set.filter(value=0)])
            votes["no"] = -sum([x.get_value() for x in self.vote_set.filter(value=-1)])
        else:
            votes["yes"] = -1
            votes["abstain"] = -1
            votes["no"] = -1
        votes["total"] = sum([x.get_value() for x in self.vote_set.all()])
        votes["count"] = self.vote_set.exclude(value=0).count()
        return votes

    def majority_reached(self):
        result = False

        if self.special_process == 'accepted_at_assembly':
            result = True
        else:
            votes = self.get_votes()
            if votes['count'] > 0:
                result = float(votes['yes']) / votes['count'] > float(self.majority_percentage) / 100

        return result


class Comment(getCreationBase('comment')):
    comment = models.TextField()
    issue = models.ForeignKey(Issue)


class Delegate(models.Model):
    polity = models.ForeignKey(Polity)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    delegate = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='delegate_user')
    base_issue = models.ForeignKey(BaseIssue)

    class Meta:
        unique_together = (('user', 'base_issue'))

    def __unicode__(self):
        return "[%s:%s] %s -> %s" % (self.type(), self.base_issue, self.user, self.delegate)

    def polity(self):
        """Gets the polity that the delegation exists within."""
        try:
            return self.base_issue.issue.polity
        except AttributeError:
            pass
        try:
            return self.base_issue.topic.polity
        except AttributeError:
            pass
        try:
            return self.base_issue.polity
        except AttributeError:
            print "ERROR: Delegate's base_issue is None, apparently"

    def result(self):
        """Work through the delegations and figure out where it ends"""
        return self.get_path()[-1].delegate

    def type(self):
        """Figure out what kind of thing is being delegated. Returns a translated string."""
        try:
            self.base_issue.issue
            return _("Issue")
        except AttributeError:
            pass
        try:
            self.base_issue.topic
            return _("Topic")
        except AttributeError:
            pass
        try:
            self.base_issue.polity
            return _("Polity")
        except AttributeError:
            print "ERROR: Delegate's base_issue is None, apparently"

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

            if item.base_issue and item.base_issue.issue:
                base_issue = item.base_issue.issue
                if base_issue and base_issue.topics:  # If this works, we are working with an "Issue"
                    for topic in base_issue.topics.all():
                        dels = user.delegate_set.filter(base_issue=topic)
                        if len(dels) > 0:
                            # TODO: FIXME
                            # Problem: Whereas an issue can belong to multiple topics, this is
                            #  basically picking the first delegation to a topic, rather than
                            #  creating weightings. Should we do weightings?
                            path.append(dels[0])
                            continue

            try:  # If this works, we are working with an "Issue"
                base_issue = item.base_issue.topic
                dels = user.delegate_set.filter(base_issue=base_issue)
                if len(dels) > 0:
                    path.append(dels[0])
                    continue
            except AttributeError:
                pass

            break

        return path


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    issue = models.ForeignKey(Issue)
    # option = models.ForeignKey(VoteOption)
    value = models.IntegerField()
    cast = models.DateTimeField(auto_now_add=True)
    power_when_cast = models.IntegerField()

    class Meta:
        unique_together = (('user', 'issue'))

    def save(self, *largs, **kwargs):
        if self.value > 1:
            self.value = 1
        elif self.value < -1:
            self.value = -1

        self.power_when_cast = self.power()
        super(Vote, self).save(*largs, **kwargs)

    def power(self):
        # Follow reverse delgation chain to discover how much power we have.
        p = 1

        return p

    def get_value(self):
        return self.power() * self.value


class Document(NameSlugBase):
    polity = models.ForeignKey(Polity)
    issues = models.ManyToManyField(Issue) # Needed for core/management/commands/refactor.py, can be deleted afterward
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    is_adopted = models.BooleanField(default=False)
    is_proposed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        return super(Document, self).save(*args, **kwargs)

    def get_versions(self):
        return DocumentContent.objects.filter(document=self).order_by('order')

    def get_contributors(self):
        return set([dc.user for dc in self.documentcontent_set.order_by('user__username')])

    # preferred_version() finds the most proper, previous documentcontent to build a new one on.
    # It prefers the latest accepted one, but if it cannot find one, it will default to the first proposed one.
    # If it finds neither a proposed nor accepted one, it will try to find the first rejected one.
    # It will return None if it finds nothing and it's the calling function's responsibility to react accordingly.
    # TODO: Make this faster and cached per request. Preferably still Pythonic. -helgi@binary.is, 2014-07-02
    def preferred_version(self):
        documentcontent = None

        # Latest accepted version...
        accepted_versions = self.documentcontent_set.filter(status='accepted').order_by('-order')
        if accepted_versions.count() > 0:
            documentcontent = accepted_versions[0]
        else:
            # ...and if none are found, find the earliest proposed one...
            proposed_versions = self.documentcontent_set.filter(status='proposed').order_by('order')
            if proposed_versions.count() > 0:
                documentcontent = proposed_versions[0]
            else:
                # ...finally and desperately going for the first rejected one.
                rejected_versions = self.documentcontent_set.filter(status='rejected').order_by('order')
                if rejected_versions.count() > 0:
                    documentcontent = rejected_versions[0]

        return documentcontent

    # Returns true if a documentcontent in this document already has an issue in progress.
    def has_open_issue(self):
        documentcontent_ids = [dc.id for dc in self.documentcontent_set.all()]
        count = Issue.objects.filter(is_processed=False, documentcontent_id__in=documentcontent_ids).count()
        return count > 0


class DocumentContent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    document = models.ForeignKey(Document)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    order = models.IntegerField(default=1)
    comments = models.TextField(blank=True)
    STATUS_CHOICES = (
        ('proposed', _('Proposed')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('deprecated', _('Deprecated')),
    )
    status = models.CharField(max_length='32', choices=STATUS_CHOICES, default='proposed')
    predecessor = models.ForeignKey('DocumentContent', null=True, blank=True)


    # Attempt to inherit earlier issue's topic selection
    def previous_topics(self):
        selected_topics = []
        if self.order > 1:
            # NOTE: This is entirely distinct from Document.preferred_version() and should not be replaced by it.
            # This function actually regards Issues, not DocumentContents, but is determined by DocumentContent as input.

            # Find the last accepted documentcontent
            prev_contents = self.document.documentcontent_set.exclude(id=self.id).order_by('-order')
            selected_topics = []
            for c in prev_contents: # NOTE: We're iterating from newest to oldest.
                if c.status == 'accepted':
                    # A previously accepted DocumentContent MUST correspond to an issue so we brutally assume so.
                    selected_topics = [t.id for t in c.issue.topics.all()]
                    break

            # If no topic list is determined from previously accepted issue, we inherit from the last Issue, if any.
            if len(selected_topics) == 0:
                for c in prev_contents:
                    try:
                        c_issue = c.issue.get()
                        selected_topics = [t.id for t in c_issue.topics.all()]
                        break;
                    except:
                        pass

        return selected_topics

    # Gets all DocumentContents which belong to the Document to which this DocumentContent belongs to.
    def siblings(self):
        siblings = DocumentContent.objects.filter(document_id=self.document_id).order_by('order')
        return siblings

    # Generates a diff between this DocumentContent and the one provided to the function.
    def diff(self, documentcontent_id):
        earlier_content = DocumentContent.objects.get(id=documentcontent_id)

        # Basic diff_match_patch thing
        dmp = diff_match_patch()

        dmp.Diff_Timeout = 0
        # dmp.Diff_EditCost = 10 # Higher value means more semantic cleanup. 4 is default which works for us right now.

        d = dmp.diff_main(earlier_content.text, self.text)

        # Calculate the diff
        dmp.diff_cleanupSemantic(d)
        result = dmp.diff_prettyHtml(d).replace('&para;', '')

        result = re.sub(r'\r<br>', r'<br>', result) # Because we're using <pre></pre> in the template, so the HTML creates two newlines.

        return result

    def __unicode__(self):
        return "DocumentContent (ID: %d)" % self.id


class ChangeProposal(getCreationBase('change_proposal')):
    document = models.ForeignKey(Document)    # Document to reference
    issue = models.ForeignKey(Issue)

    CHANGE_PROPOSAL_ACTION_CHOICES = (
        ('NEW', 'New Agreement'),
        ('CHANGE', 'Change Agreement Text'),
        ('CHANGE_TITLE', 'Change Agreement Title'),
        ('RETIRE', 'Retire Agreement'),
    )
    action = models.CharField(max_length=20, choices=CHANGE_PROPOSAL_ACTION_CHOICES)

    content = models.TextField(help_text='Content of document, or new title', **nullblank)

    def __unicode__(self):
        return 'Change Proposal: %s (content: "%s")' % (self.action, self.content_short())

    def content_short(self):
        return trim(self.content, 30)


MOTION = {
    'TALK': 1,
    'REPLY': 2,
    'CLARIFY': 3,
    'POINT': 4,
}


def get_power(user, issue):
    power = 1
    bases = [issue, issue.polity]
    bases.extend(issue.topics.all())

    # print "Getting power for user %s on issue %s" % (user, issue)
    delegations = Delegate.objects.filter(delegate=user, base_issue__in=bases)
    for i in delegations:
        power += get_power(i.user, issue)
    return power


def get_issue_power(issue, user):
    return get_power(user, issue)


# TODO: Why are these set here? Fix later..?
Issue.get_power = get_issue_power
User.get_power = get_power


class Election(NameSlugBase):
    """
    An election is different from an issue vote; it's a vote
    on people. Users, specifically.
    """

    VOTING_SYSTEMS = (
        ('schulze', 'Schulze'),
    )

    polity = models.ForeignKey(Polity)
    voting_system = models.CharField(max_length=30, verbose_name=_('Voting system'), choices=VOTING_SYSTEMS)
    deadline_candidacy = models.DateTimeField(verbose_name=_('Deadline for candidacy'))
    deadline_votes = models.DateTimeField(verbose_name=_('Deadline for votes'))

    # Sometimes elections may depend on a user having been the organization's member for an X amount of time
    # This optional field lets the vote counter disregard members who are too new.
    deadline_joined_org = models.DateTimeField(null=True, blank=True, verbose_name=_('Membership deadline'))
    is_processed = models.BooleanField(default=False)

    instructions = models.TextField(null=True, blank=True, verbose_name=_('Instructions'))

    # An election can only be processed once, since votes are deleted during the process
    class AlreadyProcessedException(Exception):
        def __init__(self, message):
            super(Election.AlreadyProcessedException, self).__init__(message)

    def process(self):
        if self.electionvote_set.count() == 0:
            raise Election.AlreadyProcessedException('Cannot process election %s (no ElectionVote found)' % self)

        ordered_candidates = self.get_ordered_candidates_from_votes()
        vote_count = self.electionvote_set.values('user').distinct().count()

        try:
            election_result = ElectionResult.objects.get(election=self)
        except ElectionResult.DoesNotExist:
            election_result = ElectionResult.objects.create(election=self, vote_count=vote_count)

        election_result.rows.all().delete()
        order = 0
        for candidate in ordered_candidates:
            order = order + 1
            election_result_row = ElectionResultRow()
            election_result_row.election_result = election_result
            election_result_row.candidate = candidate
            election_result_row.order = order
            election_result_row.save()

        self.electionvote_set.all().delete()

        self.is_processed = True
        self.save()

    def get_ordered_candidates_from_votes(self):
        if self.deadline_joined_org:
            votes = ElectionVote.objects.select_related('candidate__user').filter(election=self, user__userprofile__joined_org__lt = self.deadline_joined_org)
        else:
            votes = ElectionVote.objects.select_related('candidate__user').filter(election=self)
        candidates = Candidate.objects.select_related('user').filter(election=self)
        votemap = {}
        for vote in votes:
            if not votemap.has_key(vote.user_id):
                votemap[vote.user_id] = []
            votemap[vote.user_id].append(vote)

        manger = []
        for user_id in votemap:
            manger.append([(v.value, v.candidate) for v in votemap[user_id]])

        preference = schulze.rank_votes(manger, candidates)
        strongest_paths = schulze.compute_strongest_paths(preference, candidates)

        ordered_candidates = schulze.get_ordered_voting_results(strongest_paths)
        return ordered_candidates

    def export_openstv_ballot(self):
        return ""

    def __unicode__(self):
        return self.name

    def is_open(self):
        return not self.is_closed()

    def is_voting(self):
        if not self.deadline_candidacy or not self.deadline_votes:
            return False

        if datetime.now() > self.deadline_candidacy and datetime.now() < self.deadline_votes:
            return True

        return False

    def is_closed(self):
        if not self.deadline_votes:
            return False

        if datetime.now() > self.deadline_votes:
            return True

        return False

    def get_candidates(self):
        ctx = {}
        ctx["count"] = self.candidate_set.count()
        ctx["users"] = [{"username": x.user.username} for x in self.candidate_set.all()]
        return ctx

    def get_unchosen_candidates(self, user):
        if not user.is_authenticated():
            return Candidate.objects.filter(election=self)
        # votes = []
        votes = ElectionVote.objects.filter(election=self, user=user)
        votedcands = [x.candidate.id for x in votes]
        if len(votedcands) != 0:
            candidates = Candidate.objects.filter(election=self).exclude(id__in=votedcands).order_by('?')
        else:
            candidates = Candidate.objects.filter(election=self).order_by('?')

        return candidates

    def get_vote_count(self):
        if self.is_processed:
            return self.result.vote_count
        else:
            return self.electionvote_set.values("user").distinct().count()

    def get_vote(self, user):
        votes = []
        if not user.is_anonymous():
            votes = ElectionVote.objects.filter(election=self, user=user).order_by("value")
        return [x.candidate for x in votes]

    def get_ballots(self):
        ballot_box = []
        for voter in self.electionvote_set.values("user").distinct():
            user = User.objects.get(pk=voter["user"])
            ballot = []
            for vote in user.electionvote_set.filter(election=self).order_by('value'):
                ballot.append(vote.candidate.user.username)
            ballot_box.append(ballot)
        random.shuffle(ballot_box)
        return ballot_box


class Candidate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    election = models.ForeignKey(Election)

    def __unicode__(self):
        return str(self.user.username)

class ElectionVote(models.Model):
    election = models.ForeignKey(Election)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    candidate = models.ForeignKey(Candidate)
    value = models.IntegerField()

    class Meta:
        unique_together = (('election', 'user', 'candidate'),
                    ('election', 'user', 'value'))

    def __unicode__(self):
        return u'In %s, user %s voted for %s for seat %d' % (self.election, self.user, self.candidate, self.value)


class ElectionResult(models.Model):
    election = models.OneToOneField('Election', related_name='result')
    vote_count = models.IntegerField()


class ElectionResultRow(models.Model):
    election_result = models.ForeignKey('ElectionResult', related_name='rows')
    candidate = models.ForeignKey('Candidate')
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
