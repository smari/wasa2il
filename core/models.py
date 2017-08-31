#coding:utf-8
import re

from base_classes import NameSlugBase
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.db.models import BooleanField
from django.db.models import Case
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import When
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from registration.signals import user_registered

from diff_match_patch.diff_match_patch import diff_match_patch

nullblank = {'null': True, 'blank': True}


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
    displayname = models.CharField(max_length=255, verbose_name=_("Name"), help_text=_("The name to display on the site."), **nullblank)
    email_visible = models.BooleanField(default=False, verbose_name=_("E-mail visible"), help_text=_("Whether to display your email address on your profile page."))
    bio = models.TextField(verbose_name=_("Bio"), **nullblank)
    picture = models.ImageField(upload_to="users", verbose_name=_("Picture"), **nullblank)
    joined_org = models.DateTimeField(null=True, blank=True) # Time when user joined organization, as opposed to registered in the system

    # User settings
    language = models.CharField(max_length=6, default=settings.LANGUAGE_CODE, choices=settings.LANGUAGES, verbose_name=_("Language"))
    topics_showall = models.BooleanField(default=True, help_text=_("Whether to show all topics in a polity, or only starred."))

    def save(self, *largs, **kwargs):
        if not self.picture:
            self.picture.name = "default.jpg"
        super(UserProfile, self).save(*largs, **kwargs)

    def user_is_verified(self):
        # We require both of these be set to consider the user verified
        return (self.verified_ssn and self.verified_name)

    def __unicode__(self):
        return u'Profile for %s (%d)' % (unicode(self.user), self.user.id)


# Make sure registration creates profiles
def _create_user_profile(**kwargs):
    UserProfile.objects.get_or_create(user=kwargs['user'])

user_registered.connect(_create_user_profile)


# Monkey-patch the User.get_name() method
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
        return u'%s' % self.name

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


class Polity(BaseIssue):
    """A political entity. See the manual."""
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='polity_created_by')
    modified_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='polity_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('Polity', help_text="Parent polity", **nullblank)
    members = models.ManyToManyField(User, related_name='polities')
    officers = models.ManyToManyField(User, verbose_name=_("Officers"), related_name="officers")

    is_listed = models.BooleanField(verbose_name=_("Publicly listed?"), default=True, help_text=_("Whether the polity is publicly listed or not."))
    is_nonmembers_readable = models.BooleanField(verbose_name=_("Publicly viewable?"), default=True, help_text=_("Whether non-members can view the polity and its activities."))
    is_newissue_only_officers = models.BooleanField(verbose_name=_("Can only officers make new issues?"), default=False, help_text=_("If this is checked, only officers can create new issues. If it's unchecked, any member can start a new issue."))
    is_front_polity = models.BooleanField(verbose_name=_("Front polity?"), default=False, help_text=_("If checked, this polity will be displayed on the front page. The first created polity automatically becomes the front polity."))

    d = dict(
        editable=False,
        null=True,
        blank=True,
        )
    created_by = models.ForeignKey(User, related_name='polity_created_by', **d)
    modified_by = models.ForeignKey(User, related_name='polity_modified_by', **d)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def is_member(self, user):
        return self.members.filter(id=user.id).exists()

    def is_officer(self, user):
        return self.officers.filter(id=user.id).exists()

    # FIXME: If we want to have different folks participating in internal
    #        affairs vs. elections, this would be one place to implement that.
    def issue_voters(self):
        return self.members

    def election_voters(self):
        return self.members

    def election_potential_candidates(self):
        return self.members

    def agreements(self):
        return DocumentContent.objects.select_related(
            'document',
            'issue'
        ).filter(
            status='accepted',
            document__polity_id=self.id
        ).order_by('-issue__deadline_votes')

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


class TopicQuerySet(models.QuerySet):
    def listing_info(self, user):
        '''
        Adds information relevant to listing of topics
        '''

        topics = self
        now = datetime.now()

        if not user.is_anonymous():
            if not UserProfile.objects.get(user=user).topics_showall:
                topics = topics.filter(usertopic__user=user)

            # Annotate the user's favoriteness of topics. Note that even though
            # it's intended as a boolean, it is actually produced as an integer.
            # So it's 1/0, not True/False.
            if not user.is_anonymous():
                topics = topics.annotate(
                    favorited=Count(
                        Case(
                            When(usertopic__user=user, then=True),
                            output_field=BooleanField
                        ),
                        distinct=True
                    )
                )

        # Annotate issue count.
        topics = topics.annotate(issue_count=Count('issue', distinct=True))

        # Annotate usertopic count.
        topics = topics.annotate(usertopic_count=Count('usertopic', distinct=True))

        # Annotate counts of issues that are open and/or being voted on.
        topics = topics.annotate(
            issues_open=Count(
                Case(
                    When(issue__deadline_votes__gte=now, then=True),
                    output_field=IntegerField()
                ),
                distinct=True
            ),
            issues_voting=Count(
                Case(
                    When(Q(issue__deadline_votes__gte=now, issue__deadline_proposals__lt=now), then=True),
                    output_field=IntegerField()
                ),
                distinct=True
            )
        )

        return topics


class Topic(BaseIssue):
    """A collection of issues unified categorically."""
    objects = TopicQuerySet.as_manager()

    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='topic_created_by')
    modified_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='topic_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    polity = models.ForeignKey(Polity)
    d = dict(
        editable=False,
        null=True,
        blank=True,
        )
    created_by = models.ForeignKey(User, related_name='topic_created_by', **d)
    modified_by = models.ForeignKey(User, related_name='topic_modified_by', **d)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def new_comments(self):
        return Comment.objects.filter(issue__topics=self).order_by("-created")[:10]


class UserTopic(models.Model):
    """Whether a user likes a topic."""
    topic = models.ForeignKey(Topic)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (("topic", "user"),)


class Issue(BaseIssue):
    SPECIAL_PROCESS_CHOICES = (
        ('accepted_at_assembly', _('Accepted at assembly')),
        ('rejected_at_assembly', _('Rejected at assembly')),
    )

    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='issue_created_by')
    modified_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='issue_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    polity = models.ForeignKey(Polity)
    topics = models.ManyToManyField(Topic, verbose_name=_("Topics"))
    documentcontent = models.OneToOneField('DocumentContent', related_name='issue', **nullblank)
    deadline_discussions = models.DateTimeField(**nullblank)
    deadline_proposals = models.DateTimeField(**nullblank)
    deadline_votes = models.DateTimeField(**nullblank)
    majority_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    ruleset = models.ForeignKey(PolityRuleset, verbose_name=_("Ruleset"), editable=True)

    is_processed = models.BooleanField(default=False)
    votecount = models.IntegerField(default=0)
    votecount_yes = models.IntegerField(default=0)
    votecount_abstain = models.IntegerField(default=0)
    votecount_no = models.IntegerField(default=0)

    special_process = models.CharField(max_length=32, verbose_name=_("Special process"), choices=SPECIAL_PROCESS_CHOICES, default='', null=True, blank=True)

    d = dict(
        editable=False,
        null=True,
        blank=True,
        )

    created_by = models.ForeignKey(User, related_name='issue_created_by', **d)
    modified_by = models.ForeignKey(User, related_name='issue_modified_by', **d)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-deadline_votes"]

    def __unicode__(self):
        return u'%s' % self.name

    def apply_ruleset(self, now=None):
        now = now or datetime.now()

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

    def discussions_closed(self):
        return datetime.now() > self.deadline_discussions

    def percentage_reached(self):
        if self.votecount != 0:
            return float(self.votecount_yes) / float(self.votecount) * 100
        else:
            return 0.0

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

    def get_voters(self):
        # FIXME: This is one place to check if we've invited other groups to
        #        participate in an election, if we implement that feature...
        return self.polity.issue_voters()

    def can_vote(self, user=None, user_id=None):
        return self.get_voters().filter(
            id=(user_id if (user_id is not None) else user.id)).exists()

    def topics_str(self):
        return ', '.join(map(str, self.topics.all()))

    def proposed_documents(self):
        return self.document_set.filter(is_proposed=True)

    def user_documents(self, user):
        try:
            return self.document_set.filter(user=user)
        except TypeError:
            return []

    def majority_reached(self):
        result = False

        if self.special_process == 'accepted_at_assembly':
            result = True
        else:
            if self.votecount > 0:
                result = float(self.votecount_yes) / self.votecount > float(self.majority_percentage) / 100

        return result


class Comment(models.Model):
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='comment_created_by')
    modified_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name='comment_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    comment = models.TextField()
    issue = models.ForeignKey(Issue)

    d = dict(
        editable=False,
        null=True,
        blank=True,
        )
    created_by = models.ForeignKey(User, related_name='comment_created_by', **d)
    modified_by = models.ForeignKey(User, related_name='comment_modified_by', **d)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


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
        # Latest accepted version...
        accepted_versions = self.documentcontent_set.filter(status='accepted').order_by('-order')
        if accepted_versions.count() > 0:
            return accepted_versions[0]

        # ...and if none are found, find the earliest proposed one...
        proposed_versions = self.documentcontent_set.filter(status='proposed').order_by('order')
        if proposed_versions.count() > 0:
            return proposed_versions[0]

        # ...boo, go for the first rejected one?
        rejected_versions = self.documentcontent_set.filter(status='rejected').order_by('order')
        if rejected_versions.count() > 0:
            return rejected_versions[0]

        # ...finally and desperately search for things with unknown status
        all_versions = self.documentcontent_set.order_by('order')
        if all_versions.count() > 0:
            return all_versions[0]
        else:
            return None

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
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='proposed')
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
        return u"DocumentContent (ID: %d)" % self.id
