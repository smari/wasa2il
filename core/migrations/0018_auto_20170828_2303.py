# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20170827_1446'),
    ]

    database_operations = [
        migrations.AlterModelTable('Election', 'election_election'),
        migrations.AlterModelTable('Candidate', 'election_candidate'),
        migrations.AlterModelTable('ElectionVote', 'election_electionvote'),
        migrations.AlterModelTable('ElectionResult', 'election_electionresult'),
        migrations.AlterModelTable('ElectionResultRow', 'election_electionresultrow')
    ]

    state_operations = [
        migrations.DeleteModel('Election'),
        migrations.DeleteModel('Candidate'),
        migrations.DeleteModel('ElectionVote'),
        migrations.DeleteModel('ElectionResult'),
        migrations.DeleteModel('ElectionResultRow')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
