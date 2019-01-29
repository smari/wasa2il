#coding:utf-8
import os
import re
import json

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

import inspect

class UserProfile(models.Model):
    """A user's profile data. Contains various informative areas, plus various settings."""
    user = models.OneToOneField(User)

    # Verification
    verified_ssn = models.CharField(max_length=30, null=True, blank=True, unique=True)
    verified_name = models.CharField(max_length=100, null=True, blank=True)
    verified_token = models.CharField(max_length=100, null=True, blank=True)
    verified_timing = models.DateTimeField(null=True, blank=True)
    # When using SAML, the 'verified' field is set to true if verified_ssn,
    # verified_name and verified_timing have all been set with actual content.
    # Otherwise, it should be the same as User.is_active.
    verified = models.BooleanField(default=False)

    # User information
    displayname = models.CharField(max_length=255, verbose_name=_("Name"), help_text=_("The name to display on the site."), null=True, blank=True)
    email_visible = models.BooleanField(default=False, verbose_name=_("E-mail visible"), help_text=_("Whether to display your email address on your profile page."))
    bio = models.TextField(verbose_name=_("Bio"), null=True, blank=True)
    picture = models.ImageField(upload_to='profiles', verbose_name=_("Picture"), null=True, blank=True)
    joined_org = models.DateTimeField(null=True, blank=True) # Time when user joined organization, as opposed to registered in the system

    # When this is null (None), it means that the user has not consented to,
    # nor specifically rejected receiving email. This is a left-over state
    # from when implied consent sufficed, but should gradually be decreased
    # until all users have either consented or not. No new members should have
    # this field as null (None).
    email_wanted = models.NullBooleanField(
        default=False,
        verbose_name=_('Consent for sending email'),
        help_text=_('Whether to consent to receiving notifications via email.')
    )

    language = models.CharField(max_length=6, default='en', choices=settings.LANGUAGES, verbose_name=_("Language"))
    topics_showall = models.BooleanField(default=True, help_text=_("Whether to show all topics in a polity, or only starred."))

    def save(self, *largs, **kwargs):
        is_new = self.pk is None

        if is_new:
            self.language = settings.LANGUAGE_CODE

        if not self.picture:
            self.picture.name = os.path.join(
                self.picture.field.upload_to,
                'default.jpg'
            )

        if settings.SAML_1['URL']:
            self.verified = all((
                self.verified_ssn is not None and len(self.verified_ssn) > 0,
                self.verified_name is not None and len(self.verified_name) > 0
            ))
        else:
            self.verified = self.user.is_active

        super(UserProfile, self).save(*largs, **kwargs)

    def __unicode__(self):
        return u'Profile for %s (%d)' % (unicode(self.user), self.user.id)

    def get_polity_ids(self):
        return [x.id for x in self.user.polities.all()]

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

def tasks_applied(user):
    return user.taskrequest_set.all()

def tasks_accepted(user):
    return tasks_applied(user).filter(is_accepted=True)

def tasks_completed(user):
    return tasks_accepted(user).filter(task__is_done=True)

def tasks_percent(user):
    applied_cnt = tasks_applied(user).count()
    if applied_cnt == 0:
        return {'applied': 0, 'accepted': 0, 'completed': 100}
    accepted_cnt = tasks_accepted(user).count()
    completed_cnt = tasks_completed(user).count()
    ret = {
        'applied': 100*(applied_cnt - accepted_cnt - completed_cnt) / float(applied_cnt),
        'accepted': 100*(accepted_cnt - completed_cnt) / float(applied_cnt),
        'completed': 100*(completed_cnt) / float(applied_cnt)
    }
    return ret

User.get_name = get_name
User.tasks_applied = tasks_applied
User.tasks_accepted = tasks_accepted
User.tasks_completed = tasks_completed
User.tasks_percent = tasks_percent



class Event(models.Model):
    timestamp       = models.DateTimeField(auto_now=True)
    user            = models.ForeignKey(User, blank=True, null=True)
    module          = models.CharField(max_length=32, blank=False)
    action          = models.CharField(max_length=32, blank=False)
    category        = models.CharField(max_length=64, blank=True)
    event           = models.CharField(max_length=1024, blank=True)

    def __str__(self):
        return "[%s][%s.%s/%s@%s] %s" % (self.timestamp, self.module, self.action, self.category, self.user, self.event)

def event_register(action, category="", event={}, user=None):
    e = Event()
    e.user = user
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    e.module = mod.__name__
    e.action = action
    e.category = category
    e.event = json.dumps(event)
    e.save()

def event_time_since_last(module, action):
    e = Event.objects.filter(module=module, action=action).order_by('-timestamp')
    if len(e) == 0:
        return timedelta(100000000)
    else:
        return datetime.now() - e[0].timestamp
