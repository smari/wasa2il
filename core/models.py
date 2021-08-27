#coding:utf-8
import os
import re
import json

from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.db.models import BooleanField
from django.db.models import CASCADE
from django.db.models import Case
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import SET_NULL
from django.db.models import When
from django.contrib.auth.models import User as BaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from registration.signals import user_registered

from diff_match_patch.diff_match_patch import diff_match_patch

from issue.models import DocumentContent
from issue.models import Issue

import inspect


# See: https://docs.djangoproject.com/en/3.2/topics/db/managers/#custom-managers
class UserManager(models.Manager):
    # Annotates basic task statistics.
    def annotate_task_stats(self):
        return self.annotate(
            tasks_applied_count=Count('taskrequest'),
            tasks_completed_count=Count('taskrequest', filter=Q(taskrequest__task__is_done=True)),
            tasks_accepted_count=Count('taskrequest', filter=Q(taskrequest__is_accepted=True))
        )


# A proxy model only so that we can add our own model manager and functions
# for dealing with project-specific things.
# See: https://docs.djangoproject.com/en/3.2/topics/db/models/#proxy-models
class User(BaseUser):
    objects = UserManager()

    # Produces percentages out of task statistics produced through the
    # `annotate_task_stats()` function in our model manager.
    def tasks_percent(self):
        # Make sure that we instruct the programmer properly if they're using
        # this function without using the proper annotation function that
        # produces the required data.
        needed_attrs = ['tasks_applied_count', 'tasks_accepted_count', 'tasks_completed_count']
        if not all(hasattr(self, a) for a in needed_attrs):
            raise Exception('User.tasks_percent() function can only be called when User.objects.annotate_task_stats() has been applied')

        # Let's not bother calculating things if everything is zero anyway.
        if self.tasks_applied_count == 0:
            return {'applied': 0, 'accepted': 0, 'completed': 100}

        return {
            'applied': 100*(self.tasks_applied_count - self.tasks_accepted_count - self.tasks_completed_count) / float(self.tasks_applied_count),
            'accepted': 100*(self.tasks_accepted_count - self.tasks_completed_count) / float(self.tasks_applied_count),
            'completed': 100*(self.tasks_completed_count) / float(self.tasks_applied_count)
        }

    class Meta:
        proxy = True


class UserProfile(models.Model):
    """A user's profile data. Contains various informative areas, plus various settings."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    # Verification
    # Field `verified_token` was used with SAML 1.2 whereas
    # `verified_assertion_id` has been used since adopting SAML 2.
    verified_ssn = models.CharField(max_length=30, null=True, blank=True, unique=True)
    verified_name = models.CharField(max_length=100, null=True, blank=True)
    verified_token = models.CharField(max_length=100, null=True, blank=True)
    verified_assertion_id = models.CharField(max_length=50, null=True, blank=True)
    verified_timing = models.DateTimeField(null=True, blank=True)
    # When using SAML, the 'verified' field is set to true if verified_ssn,
    # verified_name and verified_timing have all been set with actual content.
    # Otherwise, it should be the same as User.is_active.
    verified = models.BooleanField(default=False)

    # User information
    displayname = models.CharField(max_length=255, verbose_name=_("Name"), help_text=_("The name to display on the site."), null=True, blank=True)
    phone = models.CharField(max_length=30, verbose_name=_('Phone'), help_text=_('Mostly intended for active participants such as volunteers and candidates.'),  null=True, blank=True)
    email_visible = models.BooleanField(default=False, verbose_name=_("E-mail visible"), help_text=_("Whether to display your email address on your profile page."))
    bio = models.TextField(verbose_name=_("Bio"), null=True, blank=True)
    declaration_of_interests = models.TextField(verbose_name=_('Declaration of interests'), null=True, blank=True)
    picture = models.ImageField(upload_to='profiles', verbose_name=_("Picture"), null=True, blank=True)
    joined_org = models.DateTimeField(null=True, blank=True) # Time when user joined organization, as opposed to registered in the system

    # When this is null (None), it means that the user has not consented to,
    # nor specifically rejected receiving email. This is a left-over state
    # from when implied consent sufficed, but should gradually be decreased
    # until all users have either consented or not. No new members should have
    # this field as null (None).
    email_wanted = models.BooleanField(
        default=False,
        null=True,
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

        if settings.SAML['URL']:
            self.verified = all((
                self.verified_ssn is not None and len(self.verified_ssn) > 0,
                self.verified_name is not None and len(self.verified_name) > 0
            ))
        else:
            self.verified = self.user.is_active

        super(UserProfile, self).save(*largs, **kwargs)

    def __str__(self):
        return u'Profile for %s (%d)' % (self.user, self.user.id)

    def get_polity_ids(self):
        return [x.id for x in self.user.polities.all()]

# Make sure registration creates profiles
def _create_user_profile(**kwargs):
    UserProfile.objects.get_or_create(user=kwargs['user'])

user_registered.connect(_create_user_profile)


# TODO: Deprecate this function.
# This function should be deprecated in favor of calling
# `.userprofile.displayname` directly, the reason being that this
# function hides the need for using `select_related()`, but also because
# a `UserProfile` is now automatically created so it accounts for a
# scenario that no longer occurs.
def get_name(user):
    name = ""
    if user:
        try:
            name = user.userprofile.displayname
        except AttributeError:
            print('User with id %d missing profile?' % user.id)
            pass

    if not name:
        name = user.username

    return name

# We need to monkey-patch both `BaseUser` and `User` because we've added
# `User` as a proxy model. Both monkey-patches should removed when
# `get_name` gets refactored out.
BaseUser.get_name = get_name
User.get_name = get_name


class Event(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    module = models.CharField(max_length=32, blank=False)
    action = models.CharField(max_length=32, blank=False)
    category = models.CharField(max_length=64, blank=True)
    event = models.CharField(max_length=1024, blank=True)

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
