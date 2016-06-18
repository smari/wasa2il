# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160510_0907'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location_code', models.CharField(unique=True, max_length=20)),
                ('location_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='polity',
            name='zip_codes',
        ),
        migrations.DeleteModel(
            name='ZipCode',
        ),
        migrations.AddField(
            model_name='polity',
            name='location_codes',
            field=models.ManyToManyField(to='core.LocationCode', blank=True),
        ),
    ]
