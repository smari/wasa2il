# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue', '0003_auto_20170910_1417'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField()),
                ('created_by', models.ForeignKey(related_name='comment_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('issue', models.ForeignKey(to='issue.Issue')),
                ('modified_by', models.ForeignKey(related_name='comment_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
