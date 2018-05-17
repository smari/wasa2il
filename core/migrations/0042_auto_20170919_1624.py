# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20170910_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcontent',
            name='document',
            field=models.ForeignKey(related_name='old_documentcontent_set', to='core.Document'),
        ),
        migrations.AlterField(
            model_name='documentcontent',
            name='user',
            field=models.ForeignKey(related_name='old_documentcontent_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
