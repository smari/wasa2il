# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseIssue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChangeProposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=20, choices=[(b'NEW', b'New Agreement'), (b'CHANGE', b'Change Agreement Text'), (b'CHANGE_TITLE', b'Change Agreement Title'), (b'RETIRE', b'Retire Agreement')])),
                ('content', models.TextField(help_text=b'Content of document, or new title', null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='change_proposal_created_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='comment_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(related_name='comment_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Delegate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('is_adopted', models.BooleanField(default=False)),
                ('is_proposed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='DocumentContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('order', models.IntegerField(default=1)),
                ('comments', models.TextField(blank=True)),
                ('status', models.CharField(default=b'proposed', max_length=b'32', choices=[(b'proposed', 'Proposed'), (b'accepted', 'Accepted'), (b'rejected', 'Rejected'), (b'deprecated', 'Deprecated')])),
                ('document', models.ForeignKey(to='core.Document')),
                ('predecessor', models.ForeignKey(blank=True, to='core.DocumentContent', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('voting_system', models.CharField(max_length=30, verbose_name='Voting system', choices=[(b'schulze', b'Schulze')])),
                ('deadline_candidacy', models.DateTimeField(verbose_name='Deadline for candidacy')),
                ('deadline_votes', models.DateTimeField(verbose_name='Deadline for votes')),
                ('deadline_joined_org', models.DateTimeField(null=True, verbose_name='Membership deadline', blank=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('instructions', models.TextField(null=True, verbose_name='Instructions', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ElectionResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote_count', models.IntegerField()),
                ('election', models.OneToOneField(related_name='result', to='core.Election')),
            ],
        ),
        migrations.CreateModel(
            name='ElectionResultRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('candidate', models.ForeignKey(to='core.Candidate')),
                ('election_result', models.ForeignKey(related_name='rows', to='core.ElectionResult')),
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
                ('candidate', models.ForeignKey(to='core.Candidate')),
                ('election', models.ForeignKey(to='core.Election')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PolityRuleset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('issue_quora_percent', models.BooleanField(default=False)),
                ('issue_quora', models.IntegerField()),
                ('issue_majority', models.DecimalField(max_digits=5, decimal_places=2)),
                ('issue_discussion_time', models.IntegerField()),
                ('issue_proposal_time', models.IntegerField()),
                ('issue_vote_time', models.IntegerField()),
                ('adopted_if_accepted', models.BooleanField(default=True)),
                ('confirm_with', models.ForeignKey(blank=True, to='core.PolityRuleset', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verified_ssn', models.CharField(max_length=30, unique=True, null=True, blank=True)),
                ('verified_name', models.CharField(max_length=100, null=True, blank=True)),
                ('verified_token', models.CharField(max_length=100, null=True, blank=True)),
                ('verified_timing', models.DateTimeField(null=True, blank=True)),
                ('displayname', models.CharField(help_text='The name to display on the site.', max_length=b'255', null=True, verbose_name='Name', blank=True)),
                ('email_visible', models.BooleanField(default=False, help_text='Whether to display your email address on your profile page.', verbose_name='E-mail visible')),
                ('bio', models.TextField(null=True, verbose_name='Bio', blank=True)),
                ('picture', models.ImageField(upload_to=b'users', null=True, verbose_name='Picture', blank=True)),
                ('joined_org', models.DateTimeField(null=True, blank=True)),
                ('language', models.CharField(default=b'en', max_length=b'6', verbose_name='Language', choices=[(b'is', b'\xc3\x8dslenska'), (b'en', b'English'), (b'es', b'Espa\xc3\xb1ol'), (b'fr', b'Fran\xc3\xa7aise'), (b'nl', b'Nederlands')])),
                ('topics_showall', models.BooleanField(default=True, help_text='Whether to show all topics in a polity, or only starred.')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('cast', models.DateTimeField(auto_now_add=True)),
                ('power_when_cast', models.IntegerField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ZipCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zip_code', models.CharField(unique=True, max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('baseissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.BaseIssue')),
                ('deadline_discussions', models.DateTimeField(null=True, blank=True)),
                ('deadline_proposals', models.DateTimeField(null=True, blank=True)),
                ('deadline_votes', models.DateTimeField(null=True, blank=True)),
                ('majority_percentage', models.DecimalField(max_digits=5, decimal_places=2)),
                ('is_processed', models.BooleanField(default=False)),
                ('special_process', models.CharField(default=b'', choices=[(b'accepted_at_assembly', 'Accepted at assembly'), (b'rejected_at_assembly', 'Rejected at assembly')], max_length=b'32', blank=True, null=True, verbose_name='Special process')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='issue_created_by', to=settings.AUTH_USER_MODEL)),
                ('documentcontent', models.OneToOneField(related_name='issue', null=True, blank=True, to='core.DocumentContent')),
                ('modified_by', models.ForeignKey(related_name='issue_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-deadline_votes'],
            },
            bases=('core.baseissue',),
        ),
        migrations.CreateModel(
            name='Polity',
            fields=[
                ('baseissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.BaseIssue')),
                ('is_listed', models.BooleanField(default=True, help_text='Whether the polity is publicly listed or not.', verbose_name='Publicly listed?')),
                ('is_nonmembers_readable', models.BooleanField(default=True, help_text='Whether non-members can view the polity and its activities.', verbose_name='Publicly viewable?')),
                ('is_newissue_only_officers', models.BooleanField(default=False, help_text="If this is checked, only officers can create new issues. If it's unchecked, any member can start a new issue.", verbose_name='Can only officers make new issues?')),
                ('is_front_polity', models.BooleanField(default=False, help_text='If checked, this polity will be displayed on the front page. The first created polity automatically becomes the front polity.', verbose_name='Front polity?')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='polity_created_by', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(related_name='polity_modified_by', to=settings.AUTH_USER_MODEL)),
                ('officers', models.ManyToManyField(related_name='officers', verbose_name='Officers', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, to='core.Polity', help_text=b'Parent polity', null=True)),
                ('zip_codes', models.ManyToManyField(to='core.ZipCode', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('core.baseissue',),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('baseissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.BaseIssue')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='topic_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(related_name='topic_modified_by', to=settings.AUTH_USER_MODEL)),
                ('polity', models.ForeignKey(to='core.Polity')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=('core.baseissue',),
        ),
        migrations.AddField(
            model_name='delegate',
            name='base_issue',
            field=models.ForeignKey(to='core.BaseIssue'),
        ),
        migrations.AddField(
            model_name='delegate',
            name='delegate',
            field=models.ForeignKey(related_name='delegate_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='delegate',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='changeproposal',
            name='document',
            field=models.ForeignKey(to='core.Document'),
        ),
        migrations.AddField(
            model_name='changeproposal',
            name='modified_by',
            field=models.ForeignKey(related_name='change_proposal_modified_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ForeignKey(to='core.Election'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vote',
            name='issue',
            field=models.ForeignKey(to='core.Issue'),
        ),
        migrations.AddField(
            model_name='usertopic',
            name='topic',
            field=models.ForeignKey(to='core.Topic'),
        ),
        migrations.AddField(
            model_name='polityruleset',
            name='polity',
            field=models.ForeignKey(to='core.Polity'),
        ),
        migrations.AddField(
            model_name='issue',
            name='polity',
            field=models.ForeignKey(to='core.Polity'),
        ),
        migrations.AddField(
            model_name='issue',
            name='ruleset',
            field=models.ForeignKey(verbose_name='Ruleset', to='core.PolityRuleset'),
        ),
        migrations.AddField(
            model_name='issue',
            name='topics',
            field=models.ManyToManyField(to='core.Topic', verbose_name='Topics'),
        ),
        migrations.AlterUniqueTogether(
            name='electionvote',
            unique_together=set([('election', 'user', 'candidate'), ('election', 'user', 'value')]),
        ),
        migrations.AddField(
            model_name='election',
            name='polity',
            field=models.ForeignKey(to='core.Polity'),
        ),
        migrations.AddField(
            model_name='document',
            name='issues',
            field=models.ManyToManyField(to='core.Issue'),
        ),
        migrations.AddField(
            model_name='document',
            name='polity',
            field=models.ForeignKey(to='core.Polity'),
        ),
        migrations.AlterUniqueTogether(
            name='delegate',
            unique_together=set([('user', 'base_issue')]),
        ),
        migrations.AddField(
            model_name='comment',
            name='issue',
            field=models.ForeignKey(to='core.Issue'),
        ),
        migrations.AddField(
            model_name='changeproposal',
            name='issue',
            field=models.ForeignKey(to='core.Issue'),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'issue')]),
        ),
        migrations.AlterUniqueTogether(
            name='usertopic',
            unique_together=set([('topic', 'user')]),
        ),
    ]
