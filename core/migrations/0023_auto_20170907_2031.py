# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20170907_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='polity',
            field=models.ForeignKey(to='polity.Polity'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='polity',
            field=models.ForeignKey(to='polity.Polity'),
        ),
        migrations.AlterField(
            model_name='polityruleset',
            name='polity',
            field=models.ForeignKey(to='polity.Polity'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='polity',
            field=models.ForeignKey(to='polity.Polity'),
        ),
    ]
