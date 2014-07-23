# -*- coding: utf-8 -*-
# Temporary file to fix data fuckup. Is only in repository for historical reasons and shall soon be deleted.

# IMPORTANT: Once software has been used after refactoring, DO NOT RUN THIS SCRIPT AGAIN! It WILL fuck things up!
# You have been warned!

from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import *


def real_strip_tags(content, open_tag='<', close_tag='>'):

    s = content

    search_start = 0
    index_start = s.find(open_tag, search_start)
    while index_start > -1:

        index_end = s.find(close_tag, index_start)
        if index_end > -1:
            s = s[0:index_start] + s[index_end+len(close_tag):]

        search_start = index_start
        index_start = s.find(open_tag, search_start)

    return s


class Command(BaseCommand):

    def handle(self, *args, **options):

        self.fix_grunnstefna()

        self.fix_log_pirata()

        # IMPORTANT: fix_grunnstefna() must be run before this function!
        self.kill_dead_documents()

        self.strip_document_tags() # Temporary comment, uncomment if commented!

        self.remap_issue_relations_to_documentcontent()

        self.set_documentcontent_status()

        self.kill_wonky_issues_in_hafnarfjordur()

        self.make_all_issues_processed()

        self.reconfigure_polity_rulesets()

        self.remove_documentcontent_initialversion_comments()

        self.set_documentcontent_predecessors()

        # BEFORE this is run, core/management/commands/sql/refactor_before.sql should be imported into the database.

        # AFTER this has been run, the following database modifications should be made.
        # 1. Remove Document/Issue connection (Document.issue)


    def set_documentcontent_predecessors(self):
        documentcontents = DocumentContent.objects.select_related('document').order_by('document__id', 'order')
        last_documentcontent = 0
        for documentcontent in documentcontents:
            if documentcontent.order > 1 and not documentcontent.predecessor_id:
                stdout.write("Setting predecessor of document '%s' version %d to version %d..." % (documentcontent.document.name, documentcontent.order, last_documentcontent.order))
                stdout.flush()

                documentcontent.predecessor = last_documentcontent
                documentcontent.save()

                stdout.write(" done\n")

            last_documentcontent = documentcontent

    def remove_documentcontent_initialversion_comments(self):
        documentcontents = DocumentContent.objects.select_related('document').filter(comments='Initial version')
        for documentcontent in documentcontents:
            stdout.write("Removing comment 'Initial version' from documentcontent in document '%s'..." % documentcontent.document.name)
            stdout.flush()

            documentcontent.comments = ''
            documentcontent.save()

            stdout.write(" done\n")


    def reconfigure_polity_rulesets(self):
        rulesets = PolityRuleset.objects.filter(polity__name=u'Píratar')
        for ruleset in rulesets:
            if ruleset.issue_proposal_time > 0:
                stdout.write("Setting proposal time of ruleset '%s' to 0..." % ruleset.name)
                stdout.flush()

                ruleset.issue_proposal_time = 0
                ruleset.save()

                stdout.write(" done\n")


    def kill_wonky_issues_in_hafnarfjordur(self):
        # Preserve IDs (Issue):
        # * Íþrótta- og tómstundamál: 140 (Nýrri niðurstaða, fleiri atkvæði, breytingartillaga)
        # * Menntamál: 143 (Nýrri niðurstaða)
        # * Opinn hugbúnaður: 137 (Nýrri niðurstaða, fleiri atkvæði, umræða, meiri ágreiningur)
        # * Stjórnsýsla og lýðræði: 135 (Nýrri niðurstaða, fleiri atkvæði)
        # * Skipulagsmál: 132 (Nýrri niðurstaða, fleiri atkvæði, breytingartillaga)
        # * Velferðarmál: 133 (Nýrri niðurstaða, fleiri atkvæði

        # Delete IDs (Issue):
        # * Íþrótta- og tómstundamál: 139
        # * Menntamál: 142
        # * Opinn hugbúnaður: 136
        # * Stjórnsýsla og lýðræði: 134
        # * Skipulagsmál: 131
        # * Velferðarmál: 127

        issue_ids_to_delete = [139, 142, 136, 134, 131, 127]
        issues = Issue.objects.select_related('polity').filter(polity__slug='piratar-i-hafnarfirdi', id__in=issue_ids_to_delete)
        for i in issues:
            stdout.write("Deleting deprecated issue '%s' (%d) in polity '%s'..." % (i.name, i.id, i.polity.name))
            stdout.flush()

            i.documentcontent.document.delete()

            stdout.write(" done\n")


    def make_all_issues_processed(self):
        issues = Issue.objects.filter(is_processed=False)
        for i in issues:
            stdout.write("Setting processed-status to true on issue '%s'..." % i.name)
            stdout.flush()

            i.is_processed = True
            i.save()

            stdout.write(" done\n")


    def set_documentcontent_status(self):
        documents = Document.objects.filter(is_adopted=True)
        for d in documents:
            contents = d.documentcontent_set.order_by('order')
            if contents.count() > 0:
                c = contents[0]

                if c.status != 'accepted':
                    stdout.write("Setting status of first content of document '%s' to 'accepted'..." % d.name)
                    stdout.flush()

                    c.status = 'accepted'
                    c.save()

                    stdout.write(" done\n")


    def strip_document_tags(self):
        documentcontents = DocumentContent.objects.all()

        for dc in documentcontents:
            new_text = real_strip_tags(dc.text)
            if dc.text != new_text:
                stdout.write("Stripping tags from DocumentContent %d..." % dc.id)
                stdout.flush()

                dc.text = new_text
                dc.save()

                stdout.write(" done\n")


    def remap_issue_relations_to_documentcontent(self):

        documents = Document.objects.all()
        for document in documents:

            issues = document.issues.all()
            if issues.count() > 0:
                stdout.write("Processing document '%s' (%d)..." % (document.name, document.id))
                stdout.flush()

                issue = document.issues.all()[0]
                documentcontent = document.documentcontent_set.all().order_by('order')[0]

                issue.documentcontent = documentcontent
                issue.save()

                document.issues.clear()

                stdout.write(" done\n")
                stdout.flush()


    # IMPORTANT: fix_grunnstefna() must be run before this function!
    def kill_dead_documents(self):
        documents = Document.objects.filter(is_proposed=False)
        for document in documents:
            issues = document.issues.all()
            issue_count = issues.count()

            if issue_count > 1:
                raise Exception("Document '%s' (%d) has more than one issue" % (document.name, document.id))
            elif issue_count == 1:
                issue = issues[0]

                stdout.write("Deleting unproposed, unused document '%s' (%d)..." % (document.name, document.id))
                stdout.flush()

                document.delete()

                stdout.write(" done\n")

    def fix_log_pirata(self):
        doc = Document.objects.get(name='Lög Pírata')

        if not doc.is_proposed:
            stdout.write(u"Fixing 'Lög Pírata'...")
            stdout.flush()

            doc.is_proposed = True
            doc.save()

            stdout.write(" done\n")


    def fix_grunnstefna(self):

        doc = Document.objects.get(name=u'Grunnstefna Pírata')
        issues_to_remove = doc.issues.exclude(name=doc.name)

        if issues_to_remove.count() > 0 or not doc.is_proposed:
            stdout.write(u"Fixing 'Grunnstefna Pírata'...")
            stdout.flush()

            for i in issues_to_remove:
                doc.issues.remove(i)

            doc.is_proposed = True
            doc.save()

            stdout.write(" done\n")

