# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0017_update_comment_counts'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='issue_type',
            field=models.IntegerField(default=1, choices=[(1, b'Policy'), (2, b'Bylaw'), (3, b'Resolution'), (999, b'Other')]),
        ),
    ]
