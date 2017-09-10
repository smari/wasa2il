from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Issue(models.Model):
    SPECIAL_PROCESS_CHOICES = (
        ('accepted_at_assembly', _('Accepted at assembly')),
        ('rejected_at_assembly', _('Rejected at assembly')),
    )

    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='issue_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='issue_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    polity = models.ForeignKey('polity.Polity')
    topics = models.ManyToManyField('topic.Topic', verbose_name=_('Topics'))
    documentcontent = models.OneToOneField('core.DocumentContent', related_name='issue', null=True, blank=True)
    deadline_discussions = models.DateTimeField(null=True, blank=True)
    deadline_proposals = models.DateTimeField(null=True, blank=True)
    deadline_votes = models.DateTimeField(null=True, blank=True)
    majority_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    ruleset = models.ForeignKey('polity.PolityRuleset', verbose_name=_("Ruleset"), editable=True)

    is_processed = models.BooleanField(default=False)
    votecount = models.IntegerField(default=0)
    votecount_yes = models.IntegerField(default=0)
    votecount_abstain = models.IntegerField(default=0)
    votecount_no = models.IntegerField(default=0)

    special_process = models.CharField(max_length=32, verbose_name=_("Special process"), choices=SPECIAL_PROCESS_CHOICES, default='', null=True, blank=True)

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

    def __unicode__(self):
        return u'%s' % (self.name)


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    issue = models.ForeignKey('issue.Issue')
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
