from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.models import DocumentContent
from core.models import Issue


class Polity(models.Model):
    """A political entity. See the manual."""
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='polity_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='polity_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('Polity', help_text="Parent polity", null=True, blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='polities')
    officers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Officers"), related_name="officers")

    is_listed = models.BooleanField(verbose_name=_("Publicly listed?"), default=True, help_text=_("Whether the polity is publicly listed or not."))
    is_nonmembers_readable = models.BooleanField(verbose_name=_("Publicly viewable?"), default=True, help_text=_("Whether non-members can view the polity and its activities."))
    is_newissue_only_officers = models.BooleanField(verbose_name=_("Can only officers make new issues?"), default=False, help_text=_("If this is checked, only officers can create new issues. If it's unchecked, any member can start a new issue."))
    is_front_polity = models.BooleanField(verbose_name=_("Front polity?"), default=False, help_text=_("If checked, this polity will be displayed on the front page. The first created polity automatically becomes the front polity."))

    d = dict(
        editable=False,
        null=True,
        blank=True,
        )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='polity_created_by', **d)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='polity_modified_by', **d)
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

    def __unicode__(self):
        return u'%s' % (self.name)
