# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_fill_verified_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default=b'is', max_length=6, verbose_name='Language', choices=[(b'is', b'\xc3\x8dslenska'), (b'en', b'English')]),
        ),
    ]
