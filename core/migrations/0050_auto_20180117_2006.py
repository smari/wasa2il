# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20171201_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default=b'en-US', max_length=6, verbose_name='Language', choices=[(b'is', b'\xc3\x8dslenska'), (b'en', b'English')]),
        ),
    ]
