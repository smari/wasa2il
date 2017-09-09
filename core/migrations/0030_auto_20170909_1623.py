# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20170909_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertopic',
            name='topic',
            field=models.ForeignKey(to='topic.Topic'),
        ),
    ]
