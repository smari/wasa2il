# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='DiscussionPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('discussion', models.ForeignKey(to='forum.Discussion')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('users_seen', models.ManyToManyField(related_name='seen', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('nonmembers_post', models.BooleanField(default=False)),
                ('polity', models.ForeignKey(to='core.Polity')),
            ],
        ),
        migrations.AddField(
            model_name='discussion',
            name='forum',
            field=models.ForeignKey(to='forum.Forum'),
        ),
        migrations.AddField(
            model_name='discussion',
            name='started_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
