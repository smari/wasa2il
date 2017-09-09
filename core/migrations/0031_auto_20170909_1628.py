# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20170909_1623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='baseissue_ptr',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='polity',
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
    ]
