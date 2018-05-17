# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0015_remove_document_issues'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='comment_count',
            field=models.IntegerField(default=0),
        ),
    ]
