# -*- coding: utf-8 -*-
#
# This comment will look up a list of usernames, returning names.
#
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import *


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', action='append')

    def handle(self, *args, **options):
        count = 1
        for usernames in options.get('username', [[]])[0]:
            for u in (un.strip() for un in usernames.split(',') if un):
                u = u.decode('utf-8')
                try:
                    name = User.objects.get(username=u).get_name()
                except:
                    name = '[no such user]'
                print ('%d. %s (%s)' % (count, name, u)).encode('utf-8')
                count += 1
