from django.contrib import admin

from election.models import Candidate
from election.models import Election

register = admin.site.register
register(Candidate)
register(Election)
