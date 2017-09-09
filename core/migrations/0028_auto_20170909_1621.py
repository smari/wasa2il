# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20170909_1554'),
        ('topic', '0002_copy_old_data_to_new'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='topics',
        ),
        migrations.AlterUniqueTogether(
            name='usertopic',
            unique_together=set([('new_topic', 'user')]),
        ),
        migrations.RemoveField(
            model_name='usertopic',
            name='topic',
        ),
    ]
