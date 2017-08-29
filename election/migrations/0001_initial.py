# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20170828_2303'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('voting_system', models.CharField(max_length=30, verbose_name='Voting system', choices=[(b'condorcet', 'Condorcet'), (b'schulze', 'Schulze, ordered list'), (b'schulze_old', 'Schulze, ordered list (old)'), (b'schulze_new', 'Schulze, ordered list (new)'), (b'schulze_both', 'Schulze, ordered list (both)'), (b'stcom', 'Steering Committee Election'), (b'stv1', 'STV, single winner'), (b'stv2', 'STV, two winners'), (b'stv3', 'STV, three winners'), (b'stv4', 'STV, four winners'), (b'stv5', 'STV, five winners'), (b'stv8', 'STV, eight winners'), (b'stv10', 'STV, ten winners'), (b'stonethor', 'STV partition with Schulze ranking')])),
                ('results_are_ordered', models.BooleanField(default=True, verbose_name='Results are ordered')),
                ('deadline_candidacy', models.DateTimeField(verbose_name='Deadline for candidacy')),
                ('starttime_votes', models.DateTimeField(null=True, verbose_name='Start time for votes', blank=True)),
                ('deadline_votes', models.DateTimeField(verbose_name='Deadline for votes')),
                ('deadline_joined_org', models.DateTimeField(null=True, verbose_name='Membership deadline', blank=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('instructions', models.TextField(null=True, verbose_name='Instructions', blank=True)),
                ('stats', models.TextField(null=True, verbose_name='Statistics as JSON', blank=True)),
                ('stats_limit', models.IntegerField(null=True, verbose_name='Limit how many candidates we publish stats for', blank=True)),
                ('stats_publish_ballots_basic', models.BooleanField(default=False, verbose_name='Publish basic ballot statistics')),
                ('stats_publish_ballots_per_candidate', models.BooleanField(default=False, verbose_name='Publish ballot statistics for each candidate')),
                ('stats_publish_files', models.BooleanField(default=False, verbose_name='Publish advanced statistics (downloadable)')),
                ('candidate_polities', models.ManyToManyField(related_name='remote_election_candidates', to='core.Polity', blank=True)),
                ('polity', models.ForeignKey(to='core.Polity')),
                ('voting_polities', models.ManyToManyField(related_name='remote_election_votes', to='core.Polity', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ElectionResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote_count', models.IntegerField()),
                ('election', models.OneToOneField(related_name='result', to='election.Election')),
            ],
        ),
        migrations.CreateModel(
            name='ElectionResultRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('candidate', models.ForeignKey(to='election.Candidate')),
                ('election_result', models.ForeignKey(related_name='rows', to='election.ElectionResult')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ElectionVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('candidate', models.ForeignKey(to='election.Candidate')),
                ('election', models.ForeignKey(to='election.Election')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ForeignKey(to='election.Election'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='electionvote',
            unique_together=set([('election', 'user', 'candidate'), ('election', 'user', 'value')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
