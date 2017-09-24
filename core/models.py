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
