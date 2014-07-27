#coding:utf-8
from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.copy_majority_percentages_from_rulesets()

    def copy_majority_percentages_from_rulesets(self):
        issues = Issue.objects.all()
        for i in issues:
            stdout.write("Updating percentage of issue '%s' to %d" % (i.name, i.ruleset.issue_majority))
            stdout.flush()

            i.majority_percentage = i.ruleset.issue_majority
            i.save()

            stdout.write(" done\n")
        


