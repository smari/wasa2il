# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0013_auto_20170922_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcontent',
            name='document',
            field=models.ForeignKey(to='issue.Document'),
        ),
    ]
