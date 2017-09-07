# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20170907_2031'),
        ('election', '0006_auto_20170907_2031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='polity',
            name='members',
        ),
        migrations.RemoveField(
            model_name='polity',
            name='parent',
        ),
    ]
