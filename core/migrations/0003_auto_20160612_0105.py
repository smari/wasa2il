# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160510_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='voting_system',
            field=models.CharField(max_length=30, verbose_name='Voting system', choices=[(b'condorcet', b'Condorcet'), (b'schulze', b'Schulze, Ordered list'), (b'schulze_old', b'Schulze, Ordered list (old)'), (b'schulze_new', b'Schulze, Ordered list (new)'), (b'stcom', b'Steering Committee Election'), (b'stv1', b'STV, Single winner'), (b'stv2', b'STV, Two winners'), (b'stv3', b'STV, Three winners'), (b'stv4', b'STV, Four winners'), (b'stv5', b'STV, Five winners'), (b'stv10', b'STV, Ten winners')]),
        ),
    ]
