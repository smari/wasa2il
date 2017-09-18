# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polity', '0003_polityruleset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='topic_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='topic_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('polity', models.ForeignKey(to='polity.Polity')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
