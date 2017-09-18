# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20170909_1628'),
    ]

    database_operations = [
        migrations.AlterModelTable('UserTopic', 'topic_usertopic')
    ]

    state_operations = [
        migrations.DeleteModel('UserTopic')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
