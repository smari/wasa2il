# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0003_auto_20170907_1944'),
        ('core', '0023_auto_20170907_2031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='election',
            name='candidate_polities',
        ),
        migrations.RemoveField(
            model_name='election',
            name='polity',
        ),
        migrations.RemoveField(
            model_name='election',
            name='voting_polities',
        ),
    ]
