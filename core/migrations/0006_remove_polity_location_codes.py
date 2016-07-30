# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_election_starttime_votes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='polity',
            name='location_codes',
        ),
    ]
