# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_election_results_are_ordered'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='delegate',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='delegate',
            name='base_issue',
        ),
        migrations.RemoveField(
            model_name='delegate',
            name='delegate',
        ),
        migrations.RemoveField(
            model_name='delegate',
            name='user',
        ),
        migrations.DeleteModel(
            name='Delegate',
        ),
    ]
