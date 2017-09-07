# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20170907_2255'),
    ]

    database_operations = [
        migrations.AlterModelTable('PolityRuleset', 'polity_polityruleset')
    ]

    state_operations = [
        migrations.DeleteModel('PolityRuleset')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
