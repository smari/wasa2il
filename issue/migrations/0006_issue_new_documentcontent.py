# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0005_documentcontent'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='new_documentcontent',
            field=models.OneToOneField(related_name='issue', null=True, blank=True, to='issue.DocumentContent'),
        ),
    ]
