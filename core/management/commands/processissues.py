# -*- coding: utf-8 -*-
from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        now = datetime.now()

        unprocessed_issues = Issue.objects.filter(is_processed=False).order_by('deadline_votes', 'id')

        for issue in unprocessed_issues:

            if issue.issue_state() == 'concluded':

                documentcontent = issue.documentcontent
                issue_name = issue.name.encode('utf-8')

                if documentcontent is None:
                    stdout.write("Skipping issue '%s' (%d) since it has no DocumentContent\n" % (issue_name, issue.id))
                    continue

                document = documentcontent.document

                stdout.write("Processing closed issue '%s' (%d):\n" % (issue_name, issue.id))

                documentcontent.predecessor = document.preferred_version()

                stdout.write("* Majority reached: ")
                stdout.flush()

                status = ''

                if issue.majority_reached():
                    stdout.write("yes\n")
                    status = 'accepted'

                    stdout.write("* Deprecating previously accepted versions, if any... ")
                    stdout.flush()

                    prev_contents = document.documentcontent_set.exclude(id=documentcontent.id).filter(status='accepted')
                    for c in prev_contents:
                        c.status = 'deprecated'
                        c.save()

                    stdout.write("done\n")

                else:
                    stdout.write("no\n")
                    status = 'rejected'

                stdout.write("* Setting status of document version %d to '%s'... " % (documentcontent.order, status))
                stdout.flush()

                documentcontent.status = status
                documentcontent.save()

                stdout.write("done\n")

                stdout.write("* Setting processed-status of issue to true... ")
                stdout.flush()

                issue.is_processed = True
                issue.save()

                stdout.write("done\n")


