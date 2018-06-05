# -*- coding: utf-8 -*-
from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        now = datetime.now()

        unprocessed_issues = Issue.objects.filter(
            deadline_votes__lte=now,
            is_processed=False
        ).order_by('deadline_votes', 'id')

        for issue in unprocessed_issues:
            issue_name = issue.name.encode('utf-8')

            stdout.write('Processing issue %s...' % issue_name)
            stdout.flush()

            if issue.process():
                stdout.write(' done\n')
            else:
                stdout.write(' failed!\n')
