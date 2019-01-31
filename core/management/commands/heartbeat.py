from sys import stdout, stderr

from django.core.management.base import BaseCommand

from core.utils import heartbeat

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        heartbeat is a wasa2il command intended to be run once per minute,
          for instance through a cron script. It manages things like sending
          due push notifications and cleaning things.
        """
        stdout.write('Running heartbeat...\n')
        stdout.flush()
        heartbeat()
