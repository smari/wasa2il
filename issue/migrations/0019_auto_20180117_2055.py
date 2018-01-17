# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def generate_issue_identifier(apps, schema_editor):
    Issue = apps.get_model('issue', 'Issue')

    issues = Issue.objects.order_by('polity__name', 'created')

    previous_polity_id = 0
    previous_year = 0
    current_issue_num = 0
    for issue in issues:
        # Reset issue number when a new year or new polity is run into.
        if issue.polity_id != previous_polity_id or issue.created.year != previous_year:
            current_issue_num = 0

        current_issue_num += 1

        issue.issue_num = current_issue_num
        issue.issue_year = issue.created.year
        issue.save()

        previous_polity_id = issue.polity_id
        previous_year = issue.created.year


def dummy_function(apps, schema_editor):
    # Only here so that migrations can be reversed.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0018_issue_issue_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='issue_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issue',
            name='issue_year',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.RunPython(generate_issue_identifier, dummy_function),
    ]
