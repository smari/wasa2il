# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20170907_2026'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='new_polity',
            new_name='polity',
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='new_polity',
            new_name='polity',
        ),
        migrations.RenameField(
            model_name='polityruleset',
            old_name='new_polity',
            new_name='polity',
        ),
        migrations.RenameField(
            model_name='topic',
            old_name='new_polity',
            new_name='polity',
        ),
    ]
