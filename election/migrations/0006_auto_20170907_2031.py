# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0005_auto_20170907_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='polity',
            field=models.ForeignKey(to='polity.Polity'),
        ),
    ]
