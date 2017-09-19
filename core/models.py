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

from issue.models import DocumentContent
from issue.models import Issue

nullblank = {'null': True, 'blank': True}


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


class Document(NameSlugBase):
    polity = models.ForeignKey('polity.Polity')
    issues = models.ManyToManyField('issue.Issue')
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
