# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_auto_20170922_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
