# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20170922_1635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='issues',
        ),
        migrations.RemoveField(
            model_name='document',
            name='polity',
        ),
        migrations.RemoveField(
            model_name='document',
            name='user',
        ),
        migrations.DeleteModel(
            name='Document',
        ),
    ]
