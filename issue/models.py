import re

from diff_match_patch.diff_match_patch import diff_match_patch

from django.conf import settings
from django.db import models
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class IssueQuerySet(models.QuerySet):
    def recent(self):
        return self.filter(deadline_votes__gt=timezone.now() - timezone.timedelta(days=settings.RECENT_ISSUE_DAYS))


class Issue(models.Model):
    objects = IssueQuerySet.as_manager()

    SPECIAL_PROCESS_CHOICES = (
        ('accepted_at_assembly', _('Accepted at assembly')),
        ('rejected_at_assembly', _('Rejected at assembly')),
    )

    name = models.CharField(max_length=128, verbose_name=_('Name'), help_text=_(
        'A great issue name expresses the essence of a proposal as briefly as possible.'
    ))
    slug = models.SlugField(max_length=128, blank=True)

    issue_num = models.IntegerField()
    issue_year = models.IntegerField()

    description = models.TextField(verbose_name=_("Description"), null=True, blank=True, help_text=_(
        'An issue description is usually just a copy of the proposal\'s description, but you can customize it here if you so wish.'
    ))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='issue_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='issue_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    polity = models.ForeignKey('polity.Polity')
    topics = models.ManyToManyField('topic.Topic', verbose_name=_('Topics'))

    documentcontent = models.OneToOneField('issue.DocumentContent', related_name='issue', null=True, blank=True)
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


    comment_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-deadline_votes"]
        unique_together = ['polity', 'issue_year', 'issue_num']

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, *args, **kwargs):
        # Determine issue_num and issue_year based on available data.
        if self.issue_num is None or self.issue_year is None:
            self.issue_year = timezone.now().year

            with transaction.atomic():
                try:
                    self.issue_num = Issue.objects.filter(
                        polity_id=self.polity_id,
                        issue_year=self.issue_year
                    ).order_by('-issue_num')[0].issue_num + 1
                except IndexError:
                    self.issue_num = 1

                super(Issue, self).save(*args, **kwargs)
        else:
            # No transaction needed
            super(Issue, self).save(*args, **kwargs)

    def apply_ruleset(self, now=None):
        now = now or timezone.now()

        if self.special_process:
            self.deadline_discussions = now
            self.deadline_proposals = now
            self.deadline_votes = now
        else:
            self.deadline_discussions = now + self.ruleset.issue_discussion_time
            self.deadline_proposals = self.deadline_discussions + self.ruleset.issue_proposal_time
            self.deadline_votes = self.deadline_proposals + self.ruleset.issue_vote_time

        self.majority_percentage = self.ruleset.issue_majority # Doesn't mechanically matter but should be official.

    def issue_state(self):
        # Short-hands.
        now = timezone.now()
        deadline_votes = self.deadline_votes
        deadline_proposals = self.deadline_proposals
        deadline_discussions = self.deadline_discussions

        if deadline_votes < now:
            return 'concluded'
        elif deadline_proposals < now:
            return 'voting'
        elif deadline_discussions < now:
            return 'accepting_proposals'
        else:
            return 'discussion'

    def discussions_closed(self):
        return timezone.now() > self.deadline_discussions

    def percentage_reached(self):
        if self.votecount != 0:
            return float(self.votecount_yes) / float(self.votecount) * 100
        else:
            return 0.0

    def process(self):

        # We're not interested in issues that don't have documentcontents.
        # They shouldn't actually exist, by the way. They were possible in
        # earlier versions but the system no longer offers creating them
        # except using a documentcontent. These issues should be dealt with
        # somehow, at some point.
        if self.documentcontent == None:
            return False

        # Short-hands.
        documentcontent = self.documentcontent
        document = documentcontent.document

        if self.issue_state() == 'concluded' and not self.is_processed:

            # Figure out the current documentcontent's predecessor.
            # See function for details.
            documentcontent.predecessor = document.preferred_version()

            # Figure out if issue was accepted or rejected.
            if self.majority_reached():
                documentcontent.status = 'accepted'

                # Since the new version has been accepted, deprecate
                # previously accepted versions.
                prev_contents = document.documentcontent_set.exclude(
                    id=documentcontent.id
                ).filter(status='accepted')
                for prev_content in prev_contents:
                    prev_content.status = 'deprecated'
                    prev_content.save()

                # Update the document's name, if it has been changed.
                if document.name != documentcontent.name:
                    document.name = documentcontent.name
                    document.save()

            else:
                documentcontent.status = 'rejected'

            self.vote_set.all().delete()

            self.is_processed = True

            documentcontent.save()

            self.save()

        return True


    def get_voters(self):
        # FIXME: This is one place to check if we've invited other groups to
        #        participate in an election, if we implement that feature...
        return self.polity.issue_voters()

    def can_vote(self, user=None, user_id=None):
        return self.get_voters().filter(
            id=(user_id if (user_id is not None) else user.id)).exists()

    def user_documents(self, user):
        try:
            return self.document_set.filter(user=user)
        except TypeError:
            return []

    def majority_reached(self):
        if not self.issue_state() == 'concluded' or not self.is_processed:
            return False

        result = False

        if self.special_process == 'accepted_at_assembly':
            result = True
        else:
            if self.votecount > 0:
                result = float(self.votecount_yes) / self.votecount > float(self.majority_percentage) / 100

        return result

    def update_comment_count(self):
        self.comment_count = self.comment_set.count()
        self.save()

    def __unicode__(self):
        return u'%s' % (self.name)


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    issue = models.ForeignKey('issue.Issue')
    value = models.IntegerField()
    cast = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'issue'))


class Comment(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='comment_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='comment_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    comment = models.TextField()
    issue = models.ForeignKey('issue.Issue')

    def save(self, *args, **kwargs):
        is_new = self.id is None

        super(Comment, self).save(*args, **kwargs)

        if is_new:
            self.issue.update_comment_count()

    def delete(self):
        super(Comment, self).delete()

        self.issue.update_comment_count()


class Document(models.Model):

    DOCUMENT_TYPE_CHOICES = (
        (1, _('Policy')),
        (2, _('Bylaw')),
        (3, _('Motion')),
        (999, _('Other')),
    )

    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    document_type = models.IntegerField(choices=DOCUMENT_TYPE_CHOICES, default=1)

    polity = models.ForeignKey('polity.Polity')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ["-id"]

    def get_versions(self):
        return DocumentContent.objects.filter(document=self).order_by('order')

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

    def __unicode__(self):
        return u'%s' % (self.name)


class DocumentContent(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    document = models.ForeignKey('issue.Document')
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
    predecessor = models.ForeignKey('issue.DocumentContent', null=True, blank=True)


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
