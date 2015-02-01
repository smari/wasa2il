#coding:utf-8

# This script was written only to merge a particular set of simultaneous issues (votes) with the Pirate Party's bylaws.
# It exists here in the repository's history for reasons of historicity and transparency. It will be removed.
# EXTREMELY IMPORTANT: This script assumes particular values in the data, hardcoded in the script!
# DO NOT USE THIS SCRIPT unless you know exactly what you're doing. You have been warned.

from sys import stdout, stderr
import os

from django.core.management.base import BaseCommand
from django.db.models.fields import *
from django.db.models import *

from core.models import *

class Command(BaseCommand):

    def get_documentcontent_text(self, documentcontent_id):
        filepath = '%s/bylaw_update.2014-08-15/%d.txt' % (os.path.dirname(__file__), documentcontent_id)

        if os.path.isfile(filepath):
            f = open(filepath, 'r')
            text = f.read()
            f.close()

            return text
        else:
            return ''

    def handle(self, *args, **options):

        bylaw_document = Document.objects.get(name=u'Lög Pírata')

        issues = Issue.objects.filter(deadline_votes='2014-08-15')

        for issue in issues:

            documentcontent = issue.documentcontent
            document = documentcontent.document

            print issue

            print '- Passed: %s' % ('Yes' if issue.majority_reached() else 'No')
            print '- Document ID: %d' % document.id
            print '- DocumentContent ID: %d' % documentcontent.id

            print

            new_text = self.get_documentcontent_text(documentcontent.id)
            if len(new_text) > 0 and new_text != documentcontent.text.encode('utf-8'):
                # Update text
                documentcontent.text = new_text
                documentcontent.save()
                print '* Updated text for DocumentContent %d' % documentcontent.id

                # Merge DocumentContent with bylaw's Document
                old_document = documentcontent.document # Remember the Document we will delete
                max_order_q = DocumentContent.objects.filter(document_id=bylaw_document.id).aggregate(Max('order'))

                documentcontent.document_id = bylaw_document.id # Set the Document to the bylaw's Document
                documentcontent.order = max_order_q['order__max'] + 1 # Set the order to the maximum, plus one
                documentcontent.save()
                print '* Merged DocumentContent with bylaw''s Document'

                # Delete old Document
                old_document.delete()
                print '* Deleted old Document'

                # Set Issue to non-processed so that result can be re-processed
                issue.is_processed = False
                issue.save()
                print '* Issue set to re-process'

                print

