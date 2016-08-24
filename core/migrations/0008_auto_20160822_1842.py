# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_default_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='stats',
            field=models.TextField(null=True, verbose_name='Statistics as JSON', blank=True),
        ),
        migrations.AddField(
            model_name='election',
            name='stats_limit',
            field=models.IntegerField(null=True, verbose_name='Limit how many candidates we publish stats for', blank=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='candidate_polities',
            field=models.ManyToManyField(related_name='remote_election_candidates', to='core.Polity', blank=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='starttime_votes',
            field=models.DateTimeField(null=True, verbose_name='Start time for votes', blank=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='voting_polities',
            field=models.ManyToManyField(related_name='remote_election_votes', to='core.Polity', blank=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='voting_system',
            field=models.CharField(max_length=30, verbose_name='Voting system', choices=[(b'condorcet', b'Condorcet'), (b'schulze', b'Schulze, Ordered list'), (b'schulze_old', b'Schulze, Ordered list (old)'), (b'schulze_new', b'Schulze, Ordered list (new)'), (b'schulze_both', b'Schulze, Ordered list (both)'), (b'stcom', b'Steering Committee Election'), (b'stv1', b'STV, Single winner'), (b'stv2', b'STV, Two winners'), (b'stv3', b'STV, Three winners'), (b'stv4', b'STV, Four winners'), (b'stv5', b'STV, Five winners'), (b'stv10', b'STV, Ten winners'), (b'stonethor', b'STV partition with Schulze ranking')]),
        ),
    ]
