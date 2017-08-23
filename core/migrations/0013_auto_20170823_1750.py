# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20170821_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='voting_system',
            field=models.CharField(max_length=30, verbose_name='Voting system', choices=[(b'condorcet', 'Condorcet'), (b'schulze', 'Schulze, ordered list'), (b'schulze_old', 'Schulze, ordered list (old)'), (b'schulze_new', 'Schulze, ordered list (new)'), (b'schulze_both', 'Schulze, ordered list (both)'), (b'stcom', 'Steering Committee Election'), (b'stv1', 'STV, single winner'), (b'stv2', 'STV, two winners'), (b'stv3', 'STV, three winners'), (b'stv4', 'STV, four winners'), (b'stv5', 'STV, five winners'), (b'stv8', 'STV, eight winners'), (b'stv10', 'STV, ten winners'), (b'stonethor', 'STV partition with Schulze ranking')]),
        ),
    ]
