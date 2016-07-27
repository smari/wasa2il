# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20160727_0037'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='starttime_votes',
            field=models.DateTimeField(null=True, verbose_name='Start time for votes'),
        ),
    ]
