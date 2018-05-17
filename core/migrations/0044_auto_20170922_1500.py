# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20170919_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='issues',
            field=models.ManyToManyField(related_name='old_document_set', to='issue.Issue'),
        ),
        migrations.AlterField(
            model_name='document',
            name='polity',
            field=models.ForeignKey(related_name='old_document_set', to='polity.Polity'),
        ),
        migrations.AlterField(
            model_name='document',
            name='user',
            field=models.ForeignKey(related_name='old_document_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
