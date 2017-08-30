# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discussion',
            name='forum',
        ),
        migrations.RemoveField(
            model_name='discussion',
            name='started_by',
        ),
        migrations.RemoveField(
            model_name='discussionpost',
            name='discussion',
        ),
        migrations.RemoveField(
            model_name='discussionpost',
            name='user',
        ),
        migrations.RemoveField(
            model_name='discussionpost',
            name='users_seen',
        ),
        migrations.RemoveField(
            model_name='forum',
            name='polity',
        ),
        migrations.DeleteModel(
            name='Discussion',
        ),
        migrations.DeleteModel(
            name='DiscussionPost',
        ),
        migrations.DeleteModel(
            name='Forum',
        ),
    ]
