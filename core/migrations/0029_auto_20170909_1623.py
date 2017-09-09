# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20170909_1621'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issue',
            old_name='new_topics',
            new_name='topics',
        ),
        migrations.RenameField(
            model_name='usertopic',
            old_name='new_topic',
            new_name='topic',
        ),
        migrations.AlterUniqueTogether(
            name='usertopic',
            unique_together=set([('topic', 'user')]),
        ),
    ]
