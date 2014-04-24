from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        now = datetime.now()

        closed_issues = Issue.objects.filter(deadline_votes__lt=now, document__is_proposed=True, document__is_adopted=False).distinct()

        for issue in closed_issues:

            stdout.write('Checking issue %s (%d):\n' % (issue.name, issue.id))

            stdout.write('* majority reached: ')
            stdout.flush()
            if issue.majority_reached():
                stdout.write('yes\n')

                stdout.write('* adopting documents... ')
                try:
                    documents = issue.document_set.filter(is_proposed=True, is_adopted=False)
                    for document in documents:
                        document.is_adopted = True
                        document.save()

                    stdout.write('done\n')
                except:
                    stdout.write('failed\n')
            else:
                stdout.write('no\n')



