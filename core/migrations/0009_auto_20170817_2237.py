# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160822_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='votecount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='issue',
            name='votecount_abstain',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='issue',
            name='votecount_no',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='issue',
            name='votecount_yes',
            field=models.IntegerField(default=0),
        ),
    ]
