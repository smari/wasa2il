# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0007_auto_20170928_1037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='election',
            options={'ordering': ['-deadline_votes']},
        ),
    ]
