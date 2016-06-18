# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial')
    ]

    operations = [
        migrations.CreateModel(
            name='ZipCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zip_code', models.CharField(unique=True, max_length=3)),
            ],
        ),
        migrations.AddField(
            model_name='Polity',
            name='zip_codes',
            field=models.ManyToManyField(to='core.ZipCode', blank=True)
        )
    ]
