# Run this to delete old proposals to law which never had an effect.

from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        if 'YES-I-MEAN-IT' in args:
            self.delete_obsolete_versions() # DANGEROUS
        else:
            print
            print "WARNING!"
            print "DO NOT RUN THIS UNLESS YOU KNOW WHAT YOU ARE DOING!"
            print "IT WILL MERCILESSLY DELETE ALL CHANGE PROPOSALS!"
            print "YOU HAVE BEEN WARNED!"
            print
            print "Run with option \"YES-I-MEAN-IT\" if you are 100% certain."

    def delete_obsolete_versions(self):
        versions = DocumentContent.objects.all()
        for version in versions:
            if version.order > 1:
                version.delete()

