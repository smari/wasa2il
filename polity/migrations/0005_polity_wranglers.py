# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-19 22:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polity', '0004_remove_polity_is_nonmembers_readable'),
    ]

    operations = [
        migrations.AddField(
            model_name='polity',
            name='wranglers',
            field=models.ManyToManyField(related_name='wranglers', to=settings.AUTH_USER_MODEL, verbose_name='Volunteer wranglers'),
        ),
    ]
