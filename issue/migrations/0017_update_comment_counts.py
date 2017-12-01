# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_comment_counts(apps, schema_editor):
    Issue = apps.get_model('issue', 'Issue')

    for issue in Issue.objects.all():
        issue.comment_count = issue.comment_set.count()
        issue.save()


def reverse_update_comment_counts(apps, schema_editor):
    Issue = apps.get_model('issue', 'Issue')

    for issue in Issue.objects.all():
        issue.comment_count = 0
        issue.save()


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0016_issue_comment_count'),
    ]

    operations = [
        migrations.RunPython(update_comment_counts, reverse_update_comment_counts)
    ]
