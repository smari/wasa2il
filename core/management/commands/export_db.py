import random
import string
import subprocess

from datetime import timedelta

from django.utils import timezone

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import F

from election.models import ElectionVote

from issue.models import Vote

SUPPORTED_ENGINES = ['django.db.backends.mysql']

class Command(BaseCommand):

    def handle(self, *args, **options):

        # Creates a random datetime from the beginning of 2010 to now.
        def random_time():
            lowest = timezone.datetime(2010, 1, 1)
            highest = timezone.now()
            difference = highest - lowest
            seconds = random.randint(0, int(difference.total_seconds()))
            return lowest + timedelta(seconds=seconds)

        # Creates a random string according to specifications.
        def ran(length_min, length_max=0, lc=False, uc=False, digits=False):
            if lc == uc == digits == False:
                raise Exception('ran function: At last one of parameters "lc", "uc" or "digits" must be True.')

            chars = ''
            if lc:
                chars += string.ascii_lowercase
            if uc:
                chars += string.ascii_uppercase
            if digits:
                chars += string.digits

            if length_max == 0:
                length = length_min
            else:
                length = random.randint(length_min, length_max)

            return ''.join(random.choice(chars) for _ in range(length))

        # Creates a string that alternates vowels and characters to give them
        # the impression that they might be names in an exotic language.
        def random_name():
            chars = {
                'v': 'eyuioa', # Vowels
                'c': 'qwrtpsdfghjklzxcvbnm' # Consonants,
            }
            length = random.randint(3, 10)

            result = ''
            last_type = 'c' if random.randint(0, 1) == 0 else 'v'
            while len(result) < length:
                this_type = 'c' if last_type == 'v' else 'v'
                last_type = this_type

                result += random.choice(chars[this_type])

            # Capitalize first letter.
            result = result[0].upper() + result[1:]

            return result

        # Create an exact copy of the working (default) database according to
        # the export database, which is presumabyl configured in the settings.
        self.mirror_databases()

        # Remove votes, in case an issue or election is in process.
        Vote.objects.using('export').all().delete()
        ElectionVote.objects.using('export').all().delete()

        # Replace personal data with random garbage.
        for user in User.objects.using('export').select_related('userprofile'):
            user.username = ran(6, 12, lc=True)
            user.email = '%s@%s.%s' % (ran(4, 10, lc=True), ran(4, 10, lc=True), ran(2, lc=True))
            user.date_joined = random_time()

            if hasattr(user, 'userprofile'):
                user.userprofile.verified_ssn = ran(10, digits=True)
                user.userprofile.verified_name = '%s %s' % (random_name(), random_name())
                user.userprofile.verified_token = ran(30, lc=True, uc=True, digits=True)
                user.userprofile.verified_assertion_id = ran(30, lc=True, uc=True, digits=True)
                user.userprofile.verified_timing = random_time()
                user.userprofile.bio = 'The entire bio has been replaced with this mysterious text.'
                user.userprofile.declaration_of_interests = 'The interest rate is currently around 470%.'
                user.userprofile.picture = None
                user.userprofile.joined_org = user.date_joined

                user.userprofile.displayname = user.userprofile.verified_name

                user.userprofile.save()

            user.save()


    # Create an export database, an exact replica of the default database.
    def mirror_databases(self):

        if not 'export' in settings.DATABASES:
            raise Exception('This function only works if an export database is defined in settings.')

        if settings.DATABASES['default']['ENGINE'] != settings.DATABASES['export']['ENGINE']:
            raise Exception('Database engine of default and export databases must be the same.')

        engine = settings.DATABASES['default']['ENGINE']
        username = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        db_default = settings.DATABASES['default']['NAME']
        db_export = settings.DATABASES['export']['NAME']

        if engine not in SUPPORTED_ENGINES:
            raise Exception('Database engine %s not (yet) supported for exporting.' % engine)

        if engine == 'django.db.backends.mysql':
            # Make sure that database is empty and that it exists.
            subprocess.check_output(
                ['mysql', '-u', username, '-p%s' % password, '-e', 'DROP DATABASE IF EXISTS `%s`;' % db_export]
            )
            subprocess.check_output(
                ['mysql', '-u', username, '-p%s' % password, '-e', 'CREATE DATABASE `%s`;' % db_export]
            )

            # Transfer schema and data from default database to export
            # database.
            ps = subprocess.Popen(
                ['mysqldump', db_default, '-u', username, '-p%s' % password],
                stdout=subprocess.PIPE
            )
            output = subprocess.check_output(
                ['mysql', db_export, '-u', username, '-p%s' % password],
                stdin=ps.stdout
            )
            ps.wait()

            # At this point, the export database should contain an exact
            # replica of the default database, but with personal data either
            # scrambled for anonymity or removed entirely.
