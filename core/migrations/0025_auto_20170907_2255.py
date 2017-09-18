# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20170907_2250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='polity',
            name='baseissue_ptr',
        ),
        migrations.RemoveField(
            model_name='polity',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='polity',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='polity',
            name='officers',
        ),
        migrations.DeleteModel(
            name='Polity',
        ),
    ]
