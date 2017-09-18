# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20170828_2303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='polityruleset',
            name='adopted_if_accepted',
        ),
        migrations.RemoveField(
            model_name='polityruleset',
            name='confirm_with',
        ),
        migrations.RemoveField(
            model_name='polityruleset',
            name='issue_quora',
        ),
        migrations.RemoveField(
            model_name='polityruleset',
            name='issue_quora_percent',
        ),
    ]
