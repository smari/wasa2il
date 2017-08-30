# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='candidate_polities',
            field=models.ManyToManyField(related_name='remote_election_candidates', verbose_name='Candidate polities', to='core.Polity', blank=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='voting_polities',
            field=models.ManyToManyField(related_name='remote_election_votes', verbose_name='Voting polities', to='core.Polity', blank=True),
        ),
    ]
