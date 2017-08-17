# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def count_votes(apps, schema_editor):
    Issue = apps.get_model('core', 'Issue')

    issues = Issue.objects.prefetch_related('vote_set').all()
    for issue in issues:
        issue.votecount = issue.votecount_yes = issue.votecount_abstain = issue.votecount_no = 0
        votes = issue.vote_set.all()
        for vote in votes:
            if vote.value == 1:
                issue.votecount += 1
                issue.votecount_yes += 1
            elif vote.value == 0:
                # We purposely skip adding one to the total vote count.
                issue.votecount_abstain += 1
            elif vote.value == -1:
                issue.votecount += 1
                issue.votecount_no += 1

        issue.save()

def dummy_function(apps, schema_editor):
    # We don't need to reverse anything.
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20170817_2237'),
    ]

    operations = [
        migrations.RunPython(count_votes, dummy_function),
    ]
