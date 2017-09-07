# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0004_auto_20170907_2026'),
    ]

    operations = [
        migrations.RenameField(
            model_name='election',
            old_name='new_candidate_polities',
            new_name='candidate_polities',
        ),
        migrations.RenameField(
            model_name='election',
            old_name='new_polity',
            new_name='polity',
        ),
        migrations.RenameField(
            model_name='election',
            old_name='new_voting_polities',
            new_name='voting_polities',
        ),
    ]
