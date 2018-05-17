# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0008_auto_20171019_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='deadline_candidacy',
            field=models.DateTimeField(verbose_name='Deadline for candidacies'),
        ),
    ]
