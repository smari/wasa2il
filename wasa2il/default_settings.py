# -*- coding: utf-8 -*-
# ****************************************************************************
# *         NEVER, EVER, EVER USE THIS SETTINGS FILE IN PRODUCTION!!!        *
# ****************************************************************************

# These settings are here in case no local_settings.py file is found.
from sys import stdout
import os

ALLOWED_HOSTS = ['localhost', 'wasa2il-development.herokuapp.com', 'wasa2il-staging.herokuapp.com']

DEBUG = True

ORGANIZATION_NAME = ''
INSTANCE_NAME = 'Unconfigured Wasa2il'
INSTANCE_SLUG = 'unconfiguredwasa2il'
INSTANCE_LOGO = ''
INSTANCE_URL = '' # Base URL for application, for example https://wasa2il.example.com/
INSTANCE_FACEBOOK_IMAGE = 'https://example.com/full/url/to/image.png'
INSTANCE_FACEBOOK_APP_ID = ''

# Feature knobs: features enabled if True, disabled if False
FEATURES = {
    'tasks': True,
    'topic': True,
    'push_notifications': False, # Set up GCM settings below.
}

GCM_APP_ID = ""
GCM_SENDER_ID = ""
GCM_REST_API_KEY = ""

TIME_ZONE = 'Iceland'

ALLOW_LEAVE_POLITY = False

# Age limit for participation. (Currently only works with SAML.)
AGE_LIMIT = 16

DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'
DATETIME_FORMAT_DJANGO_WIDGET = 'dd/mm/yyyy hh:ii' # django-datetime-widget

LANGUAGE_CODE = 'en-US' # For example 'en-US', 'en', 'is' etc...

RECENT_ELECTION_DAYS = 7 # Number of days in which a closed election is considered "new".
RECENT_ISSUE_DAYS = 7 # Number of days in which a closed issue is considered "new".

AUTO_LOGOUT_DELAY = 30 # User is logged out after this many minutes. Comment to disable auto-logout.

# use Docker db settings if we have this env variable
if "DOCKER_DB_HOST" in os.environ:
    stdout.write('Using Docker + mysql container database! \n')
    DATABASE_ENGINE = 'django.db.backends.mysql' # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_HOST = 'db'
    DATABASE_PORT = '3306'
    DATABASE_NAME = 'docker'
    DATABASE_USER = 'docker'
    DATABASE_PASSWORD = 'docker'
else:
    stdout.write('Using local sqlite database! \n')
    DATABASE_ENGINE = 'django.db.backends.sqlite3' # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_HOST = ''
    DATABASE_PORT = ''
    DATABASE_NAME = 'wasa2il.sqlite'
    DATABASE_USER = ''
    DATABASE_PASSWORD = ''

# Where we save anonymized ballots to, in case we need a recount.
# Set to None to not save ballots at all.
BALLOT_SAVEFILE_FORMAT = 'elections/ballots-%(voting_system)s-%(election_id)s.json'

# Put in a random sequence of characters, like '2gj129ka0a3j4f4k1jdrg3igah73hgFQOWUBVwq68fFFQg2' - but make your own
SECRET_KEY = 'ThisKeyIsSecret.DontTellAnyone'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# This must be defined for error messages to get sent when DEBUG = False
SERVER_EMAIL = 'wasa2il@example.com'

# The individuals listed here will receive error messages when DEBUG = False
ADMINS = (
    ('username', 'user@example.com'),
)
