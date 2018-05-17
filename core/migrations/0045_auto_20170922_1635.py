# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20170922_1500'),
        ('issue', '0014_auto_20170922_1559'),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS `core_statementoption`;'),
        migrations.RunSQL('DROP TABLE IF EXISTS `core_statement`;'),
    ]
