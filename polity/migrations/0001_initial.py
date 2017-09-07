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
            name='Polity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('is_listed', models.BooleanField(default=True, help_text='Whether the polity is publicly listed or not.', verbose_name='Publicly listed?')),
                ('is_nonmembers_readable', models.BooleanField(default=True, help_text='Whether non-members can view the polity and its activities.', verbose_name='Publicly viewable?')),
                ('is_newissue_only_officers', models.BooleanField(default=False, help_text="If this is checked, only officers can create new issues. If it's unchecked, any member can start a new issue.", verbose_name='Can only officers make new issues?')),
                ('is_front_polity', models.BooleanField(default=False, help_text='If checked, this polity will be displayed on the front page. The first created polity automatically becomes the front polity.', verbose_name='Front polity?')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='polity_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('members', models.ManyToManyField(related_name='polities', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(related_name='polity_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('officers', models.ManyToManyField(related_name='officers', verbose_name='Officers', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, to='polity.Polity', help_text=b'Parent polity', null=True)),
            ],
        ),
    ]
