from sys import stdout, stderr
from datetime import datetime

from django.core.management.base import BaseCommand

from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        try:

            print
            print 'WARNING! This command will permanently delete EVERY ballot of EVERY election!'
            print 'Only do this if you know what you\'re doing. You have been warned.'
            print
            response = ''
            while response != 'yes' and response != 'no':
                response = raw_input('Are you REALLY certain that you wish to proceed? (yes/no) ').lower()

            if response == 'no':
                print
                print 'Chicken.'
                print
                return

            elections = Election.objects.all()

            for election in elections:
                stdout.write('Processing election %s...' % election)

                try:
                    election.process()
                    stdout.write(' done\n')
                except Election.AlreadyProcessedException:
                    stdout.write(' already processed\n')
                except:
                    stdout.write(' failed\n')

        except KeyboardInterrupt:
            print
            quit()

