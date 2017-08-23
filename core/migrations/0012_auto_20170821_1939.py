# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20170820_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='stats_publish_ballots_basic',
            field=models.BooleanField(default=False, verbose_name='Publish basic ballot statistics'),
        ),
        migrations.AddField(
            model_name='election',
            name='stats_publish_ballots_per_candidate',
            field=models.BooleanField(default=False, verbose_name='Publish ballot statistics for each candidate'),
        ),
        migrations.AddField(
            model_name='election',
            name='stats_publish_files',
            field=models.BooleanField(default=False, verbose_name='Publish advanced statistics (downloadable)'),
        ),
    ]
