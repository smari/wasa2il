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

    description = models.TextField(verbose_name=_("Description"))
    objectives = models.TextField(verbose_name=_("Objectives"))
    requirements = models.TextField(verbose_name=_("Requirements"))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='task_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='task_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    volunteers_needed = models.IntegerField(default=1)
    estimated_hours_per_week = models.IntegerField(default=1)
    estimated_duration_weeks = models.IntegerField(default=1)

    is_done = models.BooleanField(default=False)
    is_recruiting = models.BooleanField(default=True)


class TaskCategory(models.Model):
    name = models.CharField(max_length=128)

class TaskSkill(models.Model):
    name = models.CharField(max_length=128)

class TaskRequest(models.Model):
    task = models.ForeignKey('tasks.Task')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_offered = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    whyme = models.TextField(verbose_name=_("Why me?"))
