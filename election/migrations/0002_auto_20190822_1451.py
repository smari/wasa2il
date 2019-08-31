# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-22 14:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='electionresultrow',
            name='candidate',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result_row', to='election.Candidate'),
        ),
    ]