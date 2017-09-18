# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        #('polity', '0001_initial'),
        ('core', '0020_auto_20170907_1944'),
        #('election', '0003_auto_20170907_1944'),
        ('polity', '0002_copy_polity_data'),

    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='polity',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='polity',
        ),
        migrations.RemoveField(
            model_name='polityruleset',
            name='polity',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='polity',
        ),
    ]
