# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0001_initial'),
        ('core', '0026_auto_20170907_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='new_topics',
            field=models.ManyToManyField(to='topic.Topic', verbose_name='Topics'),
        ),
        migrations.AddField(
            model_name='usertopic',
            name='new_topic',
            field=models.ForeignKey(to='topic.Topic', null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='created_by',
            field=models.ForeignKey(related_name='old_topic_created_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='modified_by',
            field=models.ForeignKey(related_name='old_topic_modified_by', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
