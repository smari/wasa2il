#coding:utf-8
from sys import stdout, stderr
from datetime import datetime
import os

from django.core import management
from django.core.management.base import BaseCommand

from core.models import *
from core.management.commands import processissues

class Command(BaseCommand):

    ruleset_name = u'Breytingar á félagslögum'

    def filepath(self, version):
        return "%s/bylaw/%s.txt" % (os.path.dirname(__file__), version)

    def handle(self, *args, **options):

        self.create_bylaw_ruleset()

        self.handle_version_1()

        self.handle_version_2()

        self.handle_version_3()

        self.handle_version_4()

        self.handle_version_5()

        self.handle_version_6()

        self.handle_version_7()


    def handle_version_7(self):
        try:
            dc = DocumentContent.objects.get(document_id=1, order=7)
        except DocumentContent.DoesNotExist:
            stdout.write("Insert bylaw version 7... ")
            stdout.flush()

            user = User.objects.get(username = 'odin')

            f = open(self.filepath('7'), 'r')
            text = f.read()
            f.close()

            f = open(self.filepath('7_comments'), 'r')
            comments = f.read()
            f.close()

            dc = DocumentContent()
            dc.document_id = 1
            dc.order = 7
            dc.user = user
            dc.text = text
            dc.comments = comments

            dc.save()

            stdout.write(" done\n")

        try:
            issue = dc.issue
        except Issue.DoesNotExist:
            stdout.write("Adapting earlier issue for bylaw version 7..")
            stdout.flush()

            issue = Issue.objects.get(name=u'Kosningar á framboðslista')

            old_document = issue.documentcontent.document

            issue.documentcontent = dc

            # We're keeping these.
            old_deadline_discussions = issue.deadline_discussions
            old_deadline_proposals = issue.deadline_proposals
            old_deadline_votes = issue.deadline_votes

            issue.ruleset = PolityRuleset.objects.get(name=self.ruleset_name)
            issue.apply_ruleset()

            issue.deadline_discussions = old_deadline_discussions
            issue.deadline_proposals = old_deadline_proposals
            issue.deadline_votes = old_deadline_votes
            issue.description = dc.comments

            issue.is_processed = False

            issue.save()

            stdout.write(" done\n")

            processissues.Command().handle()

            stdout.write("Deleting earlier document for bylaw version 7...")
            stdout.flush()

            old_document.delete()

            stdout.write(" done\n")


    def handle_version_6(self):
        try:
            dc = DocumentContent.objects.get(document_id=1, order=6)
        except DocumentContent.DoesNotExist:
            stdout.write("Insert bylaw version 6... ")
            stdout.flush()

            user = User.objects.get(username = 'bjornlevi')

            f = open(self.filepath('6'), 'r')
            text = f.read()
            f.close()

            f = open(self.filepath('6_comments'), 'r')
            comments = f.read()
            f.close()

            dc = DocumentContent()
            dc.document_id = 1
            dc.order = 6
            dc.user = user
            dc.text = text
            dc.comments = comments

            dc.save()

            stdout.write(" done\n")

        try:
            issue = dc.issue
        except Issue.DoesNotExist:
            stdout.write("Adapting earlier issue for bylaw version 6...")
            stdout.flush()

            issue = Issue.objects.get(name=u'Skilgreining virkra meðlima')

            old_document = issue.documentcontent.document

            issue.documentcontent = dc

            # We're keeping these.
            old_deadline_discussions = issue.deadline_discussions
            old_deadline_proposals = issue.deadline_proposals
            old_deadline_votes = issue.deadline_votes

            issue.ruleset = PolityRuleset.objects.get(name=self.ruleset_name)
            issue.apply_ruleset()

            issue.deadline_discussions = old_deadline_discussions
            issue.deadline_proposals = old_deadline_proposals
            issue.deadline_votes = old_deadline_votes
            issue.description = dc.comments

            issue.is_processed = False

            issue.save()

            stdout.write(" done\n")

            processissues.Command().handle()

            stdout.write("Deleting earlier document for bylaw version 6...")
            stdout.flush()

            old_document.delete()

            stdout.write(" done\n")


    def handle_version_5(self):
        try:
            dc = DocumentContent.objects.get(document_id=1, order=5)
        except DocumentContent.DoesNotExist:
            stdout.write("Insert bylaw version 5... ")
            stdout.flush()

            user = User.objects.get(username = 'bjornlevi')

            f = open(self.filepath('5'), 'r')
            text = f.read()
            f.close()

            f = open(self.filepath('5_comments'), 'r')
            comments = f.read()
            f.close()

            dc = DocumentContent()
            dc.document_id = 1
            dc.order = 5
            dc.user = user
            dc.text = text
            dc.comments = comments

            dc.save()

            stdout.write(" done\n")

        try:
            issue = dc.issue
        except Issue.DoesNotExist:
            stdout.write("Adapting earlier issue for bylaw version 5...")
            stdout.flush()

            issue = Issue.objects.get(name=u'Afgreiðsla tillagna til rafrænnar kosningar')

            old_document = issue.documentcontent.document

            issue.documentcontent = dc

            # We're keeping these.
            old_deadline_discussions = issue.deadline_discussions
            old_deadline_proposals = issue.deadline_proposals
            old_deadline_votes = issue.deadline_votes

            issue.ruleset = PolityRuleset.objects.get(name=self.ruleset_name)
            issue.apply_ruleset()

            issue.deadline_discussions = old_deadline_discussions
            issue.deadline_proposals = old_deadline_proposals
            issue.deadline_votes = old_deadline_votes
            issue.description = dc.comments

            issue.is_processed = False

            issue.save()

            stdout.write(" done\n")

            processissues.Command().handle()

            stdout.write("Deleting earlier document for bylaw version 5...")
            stdout.flush()

            old_document.delete()

            stdout.write(" done\n")


    def handle_version_4(self):
        try:
            dc = DocumentContent.objects.get(document_id=1, order=4)
        except DocumentContent.DoesNotExist:
            stdout.write("Insert bylaw version 4... ")
            stdout.flush()

            user = User.objects.get(username = 'odin')

            f = open(self.filepath('4'), 'r')
            text = f.read()
            f.close()

            f = open(self.filepath('4_comments'), 'r')
            comments = f.read()
            f.close()

            dc = DocumentContent()
            dc.document_id = 1
            dc.order = 4
            dc.user = user
            dc.text = text
            dc.comments = comments

            dc.save()

            stdout.write(" done\n")

        try:
            issue = dc.issue
        except Issue.DoesNotExist:
            stdout.write("Adapting earlier issue for bylaw version 4...")
            stdout.flush()

            issue = Issue.objects.get(name=u'Lagabreytingartillaga: Aðildarfélög')

            old_document = issue.documentcontent.document

            issue.documentcontent = dc

            # We're keeping these.
            old_deadline_discussions = issue.deadline_discussions
            old_deadline_proposals = issue.deadline_proposals
            old_deadline_votes = issue.deadline_votes

            issue.ruleset = PolityRuleset.objects.get(name=self.ruleset_name)
            issue.apply_ruleset()

            issue.deadline_discussions = old_deadline_discussions
            issue.deadline_proposals = old_deadline_proposals
            issue.deadline_votes = old_deadline_votes
            issue.description = dc.comments

            issue.is_processed = False

            issue.save()

            stdout.write(" done\n")

            processissues.Command().handle()

            stdout.write("Deleting earlier document for bylaw version 4...")
            stdout.flush()

            old_document.delete()

            stdout.write(" done\n")


    def handle_version_3(self):
        try:
            dc = DocumentContent.objects.get(document_id=1, order=3)
        except DocumentContent.DoesNotExist:
            stdout.write("Insert bylaw version 3... ")
            stdout.flush()

            user = User.objects.get(username = 'odin')

            f = open(self.filepath('3'), 'r')
            text = f.read()
            f.close()

            f = open(self.filepath('3_comments'), 'r')
            comments = f.read()
            f.close()

            dc = DocumentContent()
            dc.document_id = 1
            dc.order = 3
            dc.user = user
            dc.text = text
            dc.comments = comments

            dc.save()

            stdout.write(" done\n")

        bylaw_datetime = '2013-08-31 14:00:00'
        try:
            issue = dc.issue
        except Issue.DoesNotExist:
            stdout.write("Creating issue for bylaw version 3...")
            stdout.flush()

            issue = Issue()
            issue.polity = dc.document.polity
            issue.documentcontent = dc

            issue.ruleset = PolityRuleset.objects.get(name=self.ruleset_name)
            issue.apply_ruleset()

            issue.deadline_discussions = bylaw_datetime
            issue.deadline_proposals = bylaw_datetime
            issue.deadline_votes = bylaw_datetime
            issue.special_process = 'accepted_at_assembly'
            issue.name = u'Birtingar breytingartillagna á lögum Pírata'
            issue.description = dc.comments

            issue.save()

            stdout.write(" done\n")

            processissues.Command().handle()


    def handle_version_2(self):
        try:
            dc = DocumentContent.objects.get(document_id=1, order=2)
        except DocumentContent.DoesNotExist:
            stdout.write("Insert bylaw version 2... ")
            stdout.flush()

            user = User.objects.get(username = 'odin')

            f = open(self.filepath('2'), 'r')
            text = f.read()
            f.close()

            f = open(self.filepath('2_comments'), 'r')
            comments = f.read()
            f.close()

            dc = DocumentContent()
            dc.document_id = 1
            dc.order = 2
            dc.user = user
            dc.text = text
            dc.comments = comments

            dc.save()

            stdout.write(" done\n")

        bylaw_datetime = '2013-08-31 14:00:00'
        try:
            issue = dc.issue
        except Issue.DoesNotExist:
            stdout.write("Creating issue for bylaw version 2...")
            stdout.flush()

            issue = Issue()
            issue.polity = dc.document.polity
            issue.documentcontent = dc

            issue.ruleset = PolityRuleset.objects.get(name=self.ruleset_name)
            issue.apply_ruleset()

            issue.deadline_discussions = bylaw_datetime
            issue.deadline_proposals = bylaw_datetime
            issue.deadline_votes = bylaw_datetime
            issue.special_process = 'accepted_at_assembly'
            issue.name = u'Breytingar á lögum Pírata með kosningakerfi'
            issue.description = dc.comments

            issue.save()

            stdout.write(" done\n")

            processissues.Command().handle()

    def handle_version_1(self):
        f = open(self.filepath(1), 'r')
        text = f.read()
        f.close()

        dc = DocumentContent.objects.get(document_id=1, order=1)

        if dc.text.encode('utf-8') != text:
            stdout.write("Setting content of bylaw version 1...")
            stdout.flush()

            dc.text = text
            dc.save()

            stdout.write(" done\n")

        issue = dc.issue
        if not issue.special_process:
            stdout.write("Setting special_process of bylaw version 1 issue to 'accepted_at_assembly'...")
            stdout.flush()

            issue.special_process = 'accepted_at_assembly'
            issue.save()

            stdout.write(" done\n")

        bylaw_datetime = '2012-11-24 14:00:00'
        if issue.deadline_votes.strftime('%Y-%m-%d %H:%M:%S') != bylaw_datetime:
            stdout.write("Setting timing of bylaw version 1 issue to %s..." % bylaw_datetime)
            stdout.flush()

            issue.deadline_votes = bylaw_datetime
            issue.deadline_proposals = bylaw_datetime
            issue.deadline_discussions = bylaw_datetime
            issue.save()

            stdout.write(" done\n")


    def create_bylaw_ruleset(self):
        try:
            bylaw_ruleset = PolityRuleset.objects.get(name=self.ruleset_name)
        except PolityRuleset.DoesNotExist:
            stdout.write("Creating bylaw ruleset...")
            stdout.flush()

            bylaw_ruleset = PolityRuleset()
            bylaw_ruleset.polity_id = 1
            bylaw_ruleset.name = self.ruleset_name
            bylaw_ruleset.issue_quora_percent = True
            bylaw_ruleset.issue_quora = 5
            bylaw_ruleset.issue_majority = 66.67
            bylaw_ruleset.issue_discussion_time = 0
            bylaw_ruleset.issue_proposal_time = 0
            bylaw_ruleset.issue_vote_time = 518400
            bylaw_ruleset.adopted_if_accepted = True
            bylaw_ruleset.save()

            stdout.write(" done\n")


