# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_delete_locationcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='changeproposal',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='changeproposal',
            name='document',
        ),
        migrations.RemoveField(
            model_name='changeproposal',
            name='issue',
        ),
        migrations.RemoveField(
            model_name='changeproposal',
            name='modified_by',
        ),
        migrations.DeleteModel(
            name='ChangeProposal',
        ),
    ]
