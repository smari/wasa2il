# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20170910_1241'),
        ('issue', '0002_copy_old_data_to_new'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='issue',
        ),
        migrations.RemoveField(
            model_name='document',
            name='issues',
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'new_issue')]),
        ),
        migrations.RemoveField(
            model_name='vote',
            name='issue',
        ),
    ]
