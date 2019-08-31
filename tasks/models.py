from django.conf import settings
from django.db import models

from django.utils.translation import ugettext_lazy as _


TASK_CATEGORIES = (
    (1, _('Equality')),
    (2, _('Education')),
    (3, _('Justice and Law Enforcement')),
    (4, _('Economy')),
    (5, _('Healthcare')),
    (6, _('Housing')),
    (7, _('Welfare')),
    (8, _('Culture')),
    (9, _('Industry')),
    (10, _('Public finances')),
    (11, _('Transportation')),
    (12, _('Governance')),
    (13, _('Municipal affairs')),
    (14, _('Environment')),
    (15, _('Foreign affairs')),
    (16, _('Defence')),
)

TASK_SKILLS = (
    (1, _('Physical work')),
    (2, _('Training')),
    (3, _('Design')),
    (4, _('Research')),
    (5, _('Volunteer coordination')),
    (6, _('Grassroots organizing')),
    (7, _('Legal writing')),
    (8, _('Writing and editing')),
    (9, _('Policy drafting')),
    (10, _('Public representation')),
    (11, _('Technical development')),
    (12, _('Management')),
    (13, _('Planning and execution')),
    (14, _('Translating'))
)

class Task(models.Model):
    polity = models.ForeignKey('polity.Polity')
    categories = models.ManyToManyField('tasks.TaskCategory')
    skills = models.ManyToManyField('tasks.TaskSkill')

    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    objectives = models.CharField(max_length=200, verbose_name=_("Objectives"))
    description = models.TextField(verbose_name=_("Description"))
    requirements = models.TextField(verbose_name=_("Requirements"))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='task_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='task_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    volunteers_needed = models.IntegerField(default=1, verbose_name=_('Number of volunteers needed'))
    estimated_hours_per_week = models.IntegerField(default=1, verbose_name=_('Estimated hours per week'))
    estimated_duration_weeks = models.IntegerField(default=1, verbose_name=_('Estimated number of weeks'))

    is_done = models.BooleanField(default=False)
    is_recruiting = models.BooleanField(default=True, verbose_name=_('Is recruiting'))

    def accepted_volunteers(self):
        return self.taskrequest_set.filter(is_accepted=True).select_related('user')

    def applied_volunteers(self):
        return self.taskrequest_set.select_related('user')


class TaskCategory(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class TaskSkill(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class TaskRequest(models.Model):
    task = models.ForeignKey('tasks.Task')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_offered = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    whyme = models.TextField(verbose_name=_("Why me?"))
    available_time = models.TextField(verbose_name=_('What available time do I have?'))
