# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_delete_baseissue'),
    ]

    database_operations = [
        migrations.AlterModelTable('Comment', 'issue_comment')
    ]

    state_operations = [
        migrations.DeleteModel('Comment')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
