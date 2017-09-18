# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20170910_1325'),
    ]

    database_operations = [
        migrations.AlterModelTable('Vote', 'issue_vote')
    ]

    state_operations = [
        migrations.DeleteModel('Vote')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
