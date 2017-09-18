# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polity', '0001_initial'),
        ('election', '0002_auto_20170830_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='new_candidate_polities',
            field=models.ManyToManyField(related_name='remote_election_candidates', verbose_name='Candidate polities', to='polity.Polity', blank=True),
        ),
        migrations.AddField(
            model_name='election',
            name='new_polity',
            field=models.ForeignKey(default=None, to='polity.Polity', null=True),
        ),
        migrations.AddField(
            model_name='election',
            name='new_voting_polities',
            field=models.ManyToManyField(related_name='remote_election_votes', verbose_name='Voting polities', to='polity.Polity', blank=True),
        ),
    ]
