# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20160617_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='candidate_polities',
            field=models.ManyToManyField(related_name='remote_election_candidates', to='core.Polity'),
        ),
        migrations.AddField(
            model_name='election',
            name='voting_polities',
            field=models.ManyToManyField(related_name='remote_election_votes', to='core.Polity'),
        ),
        migrations.AlterField(
            model_name='polity',
            name='members',
            field=models.ManyToManyField(related_name='polities', to=settings.AUTH_USER_MODEL),
        ),
    ]
