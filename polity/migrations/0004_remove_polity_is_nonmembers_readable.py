# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polity', '0003_polityruleset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='polity',
            name='is_nonmembers_readable',
        ),
    ]
