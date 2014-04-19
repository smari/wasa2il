# Run this to fix various data discrepancies and problems.
# One day, this file should become unnecessary.

from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        self.fill_deadline_discussions()

    # When creating an issue, the field deadline_discussions is
    # expected to exist by the code, but it doesn't exist in the
    # model, nor does it have an impact on how the system works
    # except that it delays deadline_propoals by the amount that
    # should be saved in deadline_discussions.
    # Observe the following lines in core/views.py, in the
    # IssueCreateView class.
    #
    #    self.object.deadline_discussions = datetime.now() + timedelta(seconds=self.object.ruleset.issue_discussion_time)
    #    self.object.deadline_proposals = self.object.deadline_discussions + timedelta(seconds=self.object.ruleset.issue_proposal_time)
    #    self.object.deadline_votes = self.object.deadline_proposals + timedelta(seconds=self.object.ruleset.issue_vote_time)
    #
    # Assuming that the database administrator has created the
    # proper field, core_issue.deadline_discussions, this
    # function fills that field according to the values found
    # in the corresponding polity's ruleset.
    def fill_deadline_discussions(self):
        no_deadline_issues = Issue.objects.filter(deadline_discussions = None)
        for issue in no_deadline_issues:
            issue.deadline_discussions = issue.deadline_proposals - timedelta(seconds=issue.ruleset.issue_discussion_time)
            issue.save()
