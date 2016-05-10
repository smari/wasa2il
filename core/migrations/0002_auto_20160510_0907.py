# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeproposal',
            name='created_by',
            field=models.ForeignKey(related_name='change_proposal_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='changeproposal',
            name='modified_by',
            field=models.ForeignKey(related_name='change_proposal_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_by',
            field=models.ForeignKey(related_name='comment_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='modified_by',
            field=models.ForeignKey(related_name='comment_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='created_by',
            field=models.ForeignKey(related_name='issue_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='modified_by',
            field=models.ForeignKey(related_name='issue_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='polity',
            name='created_by',
            field=models.ForeignKey(related_name='polity_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='polity',
            name='modified_by',
            field=models.ForeignKey(related_name='polity_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='created_by',
            field=models.ForeignKey(related_name='topic_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='modified_by',
            field=models.ForeignKey(related_name='topic_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
