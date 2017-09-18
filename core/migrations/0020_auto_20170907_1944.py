# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('polity', '0001_initial'),
        ('core', '0019_auto_20170906_0610'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='new_polity',
            field=models.ForeignKey(default=None, to='polity.Polity', null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='new_polity',
            field=models.ForeignKey(default=None, to='polity.Polity', null=True),
        ),
        migrations.AddField(
            model_name='polityruleset',
            name='new_polity',
            field=models.ForeignKey(default=None, to='polity.Polity', null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='new_polity',
            field=models.ForeignKey(default=None, to='polity.Polity', null=True),
        ),
        migrations.AlterField(
            model_name='polity',
            name='created_by',
            field=models.ForeignKey(related_name='old_polity_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='polity',
            name='members',
            field=models.ManyToManyField(related_name='old_polities', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='polity',
            name='modified_by',
            field=models.ForeignKey(related_name='old_polity_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='polity',
            name='officers',
            field=models.ManyToManyField(related_name='old_officers', verbose_name='Officers', to=settings.AUTH_USER_MODEL),
        ),
    ]
