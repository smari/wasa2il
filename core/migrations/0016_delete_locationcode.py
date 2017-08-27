# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20170827_1438'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LocationCode',
        ),
    ]
