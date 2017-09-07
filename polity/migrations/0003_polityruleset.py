# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polity', '0002_copy_polity_data'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='PolityRuleset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('issue_majority', models.DecimalField(max_digits=5, decimal_places=2)),
                ('issue_discussion_time', models.IntegerField()),
                ('issue_proposal_time', models.IntegerField()),
                ('issue_vote_time', models.IntegerField()),
                ('polity', models.ForeignKey(to='polity.Polity')),
            ],
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
