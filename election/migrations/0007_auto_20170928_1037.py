# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0006_auto_20170907_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='deadline_candidacy',
            field=models.DateTimeField(verbose_name='Candidacies accepted until'),
        ),
        migrations.AlterField(
            model_name='election',
            name='deadline_votes',
            field=models.DateTimeField(verbose_name='Election ends'),
        ),
        migrations.AlterField(
            model_name='election',
            name='starttime_votes',
            field=models.DateTimeField(null=True, verbose_name='Election begins', blank=True),
        ),
    ]
