# -*- coding: utf-8 -*-
# ****************************************************************************
# *         NEVER, EVER, EVER USE THIS SETTINGS FILE IN PRODUCTION!!!        *
# ****************************************************************************

# These settings are here in case no local_settings.py file is found.

ALLOWED_HOSTS = ['localhost', 'wasa2il-development.herokuapp.com', 'wasa2il-staging.herokuapp.com']

DEBUG = True

ORGANIZATION_NAME = ''
INSTANCE_NAME = ''
INSTANCE_SLUG = ''
INSTANCE_LOGO = ''
INSTANCE_URL = '' # Base URL for application, for example https://wasa2il.example.com/
INSTANCE_FACEBOOK_IMAGE = 'https://example.com/full/url/to/image.png'
INSTANCE_FACEBOOK_APP_ID = ''

# Feature knobs: features enabled if True, disabled if False
FEATURES = {
    'tasks': True
}

TIME_ZONE = 'Iceland'

ALLOW_LEAVE_POLITY = False

DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'
DATETIME_FORMAT_DJANGO_WIDGET = 'dd/mm/yyyy hh:ii' # django-datetime-widget

LANGUAGE_CODE = 'en-US' # For example 'en-US', 'en', 'is' etc...

RECENT_ELECTION_DAYS = 7 # Number of days in which a closed election is considered "new".
RECENT_ISSUE_DAYS = 7 # Number of days in which a closed issue is considered "new".

AUTO_LOGOUT_DELAY = 30 # User is logged out after this many minutes. Comment to disable auto-logout.

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
