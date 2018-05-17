# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0014_auto_20170922_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='issues',
        ),
    ]
