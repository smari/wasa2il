from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        now = datetime.now()

        issues = Issue.objects.all()
        for i in issues:
            if i.deadline_votes > now:

                stdout.write("Setting closing time of issue '%s' to now..." % i.name)
                stdout.flush()

                i.deadline_votes = now
                if i.deadline_proposals > i.deadline_votes:
                    i.deadline_proposals = i.deadline_votes
                if i.deadline_discussions > i.deadline_proposals:
                    i.deadline_discussions = i.deadline_proposals

                i.save()

                stdout.write(" done\n")

