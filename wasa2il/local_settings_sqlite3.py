# -*- coding: utf-8 -*-

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['example.com']

DEBUG = True

INSTANCE_NAME = ''
INSTANCE_SLUG = ''
INSTANCE_LOGO = ''

TIME_ZONE = 'Iceland'

ALLOW_LEAVE_POLITY = False

DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'

LANGUAGE_CODE = 'en-US' # For example 'en-US', 'en', 'is' etc...

# Uncomment the following to enable SAML 1.2 support (originally implemented for the "Icekey" in Iceland)
#SAML_1 = {
#    'URL': 'https://innskraning.island.is/?id=audkenni.piratar.is&path=/accounts/verify/',
#    'AUTH': {
#        'wsdl': 'https://egov.webservice.is/sst/runtime.asvc/com.actional.soapstation.eGOVDKM_AuthConsumer.AccessPoint?WSDL',
#        'login': 'some_login',
#        'password': 'some_password',
#    }
#}

# Uncomment the following to enable IcePirate support
#ICEPIRATE = {
#    'url': 'http://path-to-icepirate',
#    'key': 'some-random-string',
#}

AUTO_LOGOUT_DELAY = 30 # User is logged out after this many minutes. Comment to disable auto-logout.

DATABASE_ENGINE = 'django.db.backends.sqlite3' # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_HOST = ''
DATABASE_PORT = ''
DATABASE_NAME = 'test'
DATABASE_USER = ''
DATABASE_PASSWORD = ''

# Put in a random sequence of characters, like '2gj129ka0a3j4f4k1jdrg3igah73hgFQOWUBVwq68fFFQg2' - but make your own
SECRET_KEY = ''

#EMAIL_HOST = ''
#EMAIL_PORT = ''
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''
#EMAIL_USE_TLS = True

# This must be defined for error messages to get sent when DEBUG = False
SERVER_EMAIL = 'wasa2il@example.com'

# The individuals listed here will receive error messages when DEBUG = False
ADMINS = (
    ('username', 'user@example.com'),
)
