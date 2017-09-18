# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20170910_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='issue',
            field=models.ForeignKey(to='issue.Issue'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='issue',
            field=models.ForeignKey(to='issue.Issue'),
        ),
    ]
