# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20170823_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='results_are_ordered',
            field=models.BooleanField(default=True, verbose_name='Results are ordered'),
        ),
    ]
