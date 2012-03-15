
from django.contrib import admin

from models import Polity, Topic, Issue

register = admin.site.register

register(Polity)
register(Topic)
register(Issue)
