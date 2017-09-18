# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20170910_1248'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='new_issue',
            new_name='issue',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='new_issues',
            new_name='issues',
        ),
        migrations.RenameField(
            model_name='vote',
            old_name='new_issue',
            new_name='issue',
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'issue')]),
        ),
    ]
