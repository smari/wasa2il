# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20170919_1624'),
        ('issue', '0008_remove_issue_documentcontent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentcontent',
            name='document',
        ),
        migrations.RemoveField(
            model_name='documentcontent',
            name='predecessor',
        ),
        migrations.RemoveField(
            model_name='documentcontent',
            name='user',
        ),
        migrations.DeleteModel(
            name='DocumentContent',
        ),
    ]
