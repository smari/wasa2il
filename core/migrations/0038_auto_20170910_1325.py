# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20170910_1325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='baseissue_ptr',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='documentcontent',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='ruleset',
        ),
        migrations.DeleteModel(
            name='Issue',
        ),
    ]
