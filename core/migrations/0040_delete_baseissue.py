# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20170910_1415'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BaseIssue',
        ),
    ]
