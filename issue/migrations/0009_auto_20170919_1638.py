# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20170919_1635'),
        ('issue', '0008_remove_issue_documentcontent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issue',
            old_name='new_documentcontent',
            new_name='documentcontent',
        ),
    ]
