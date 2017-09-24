# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0012_remove_documentcontent_document'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentcontent',
            old_name='new_document',
            new_name='document',
        ),
    ]
