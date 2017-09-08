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
        migrations.RemoveField(
            model_name='polityruleset',
            name='polity',
        ),
        migrations.AlterField(
            model_name='issue',
            name='ruleset',
            field=models.ForeignKey(verbose_name='Ruleset', to='polity.PolityRuleset'),
        ),
        migrations.DeleteModel('PolityRuleset')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
