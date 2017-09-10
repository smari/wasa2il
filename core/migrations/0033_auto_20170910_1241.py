# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0001_initial'),
        ('core', '0032_auto_20170909_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='new_issue',
            field=models.ForeignKey(to='issue.Issue', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='new_issues',
            field=models.ManyToManyField(to='issue.Issue'),
        ),
        migrations.AddField(
            model_name='vote',
            name='new_issue',
            field=models.ForeignKey(to='issue.Issue', null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='created_by',
            field=models.ForeignKey(related_name='old_issue_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='documentcontent',
            field=models.OneToOneField(related_name='old_issue', null=True, blank=True, to='core.DocumentContent'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='modified_by',
            field=models.ForeignKey(related_name='old_issue_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='polity',
            field=models.ForeignKey(related_name='old_issue_set', to='polity.Polity'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='ruleset',
            field=models.ForeignKey(related_name='old_issue_set', verbose_name='Ruleset', to='polity.PolityRuleset'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='topics',
            field=models.ManyToManyField(related_name='old_issue_set', verbose_name='Topics', to='topic.Topic'),
        ),
    ]
