# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0003_auto_20170909_1719'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0032_auto_20170909_1716'),
        ('polity', '0003_polityruleset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('deadline_discussions', models.DateTimeField(null=True, blank=True)),
                ('deadline_proposals', models.DateTimeField(null=True, blank=True)),
                ('deadline_votes', models.DateTimeField(null=True, blank=True)),
                ('majority_percentage', models.DecimalField(max_digits=5, decimal_places=2)),
                ('is_processed', models.BooleanField(default=False)),
                ('votecount', models.IntegerField(default=0)),
                ('votecount_yes', models.IntegerField(default=0)),
                ('votecount_abstain', models.IntegerField(default=0)),
                ('votecount_no', models.IntegerField(default=0)),
                ('special_process', models.CharField(default=b'', choices=[(b'accepted_at_assembly', 'Accepted at assembly'), (b'rejected_at_assembly', 'Rejected at assembly')], max_length=32, blank=True, null=True, verbose_name='Special process')),
                ('created_by', models.ForeignKey(related_name='issue_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('documentcontent', models.OneToOneField(related_name='issue', null=True, blank=True, to='core.DocumentContent')),
                ('modified_by', models.ForeignKey(related_name='issue_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('polity', models.ForeignKey(to='polity.Polity')),
                ('ruleset', models.ForeignKey(verbose_name='Ruleset', to='polity.PolityRuleset')),
                ('topics', models.ManyToManyField(to='topic.Topic', verbose_name='Topics')),
            ],
            options={
                'ordering': ['-deadline_votes'],
            },
        ),
    ]
