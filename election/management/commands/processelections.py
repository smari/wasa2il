from sys import stdout, stderr
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from election.models import Election


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('election_id', nargs='*', type=int)

    def handle(self, *args, **options):

        try:
            if not settings.BALLOT_SAVEFILE_FORMAT:
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

            elections = Election.objects.filter(is_processed=False)

            for election in elections:
                if (options.get('election_id') and
                        election.id not in options['election_id']):
                    stdout.write('Skipping election %s (%s)\n' % (election, election.id))
                    continue

                stdout.write('Processing election %s...' % election)

                try:
                    election.process()
                    stdout.write(' done\n')
                except Election.AlreadyProcessedException:
                    stdout.write(' already processed\n')
                except Election.ElectionInProgressException:
                    stdout.write(' still in progress\n')
                except:
                    stdout.write(' failed for unknown reasons\n')

        except KeyboardInterrupt:
            print
            quit()

