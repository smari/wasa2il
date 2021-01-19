#coding:utf-8
# Django settings for wasa2il project.

import os
from wasa2il.utils import here
from datetime import datetime
from hashlib import sha256

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

## Base configuration
DEBUG=os.environ.get('W2_DEBUG', True)
ALLOWED_HOSTS=os.environ.get('W2_ALLOWED_HOSTS', 'localhost').split(',')

ADMINS=os.environ.get('W2_ADMINS', 'username,user@example.com').split(',')

# Contact email address
CONTACT_EMAIL=os.environ.get('W2_CONTACT_EMAIL', 'contact@example.com')

BALLOT_SAVEFILE_FORMAT=os.environ.get('W2_BALLOT_SAVEFILE_FORMAT', 'elections/ballots-%(voting_system)s-%(election_id)s.json')

## Security settings
if not os.environ.get('W2_SECRET_KEY'):
    print("You must configure the environment variable $W2_SECRET_KEY. It must be a long, hard to guess string.")
    print("To generate one, try running 'head /dev/urandom | sha256sum'.")
    exit()
SECRET_KEY=os.environ.get('W2_SECRET_KEY')
AUTO_LOGOUT_DELAY=int(os.environ.get('W2_AUTO_LOGOUT_DELAY', 30))

## Instance identity
INSTANCE_LOGO=os.environ.get('W2_INSTANCE_LOGO', '')
INSTANCE_NAME=os.environ.get('W2_INSTANCE_NAME', 'Unconfigured Wasa2il')
INSTANCE_SLUG=os.environ.get('W2_INSTANCE_SLUG', 'unconfiguredwasa2il')
INSTANCE_URL=os.environ.get('W2_INSTANCE_URL', '')
ORGANIZATION_NAME=os.environ.get('W2_ORGANIZATION_NAME', 'orgName')
ORGANIZATION_NEWS_URL=os.environ.get('W2_ORGANIZATION_NEWS_URL', '')

## Overall instance rules
AGE_LIMIT=int(os.environ.get('W2_AGE_LIMIT', 16))
ALLOW_LEAVE_POLITY=os.environ.get('W2_ALLOW_LEAVE_POLITY', False)
RECENT_ELECTION_DAYS=int(os.environ.get('W2_RECENT_ELECTION_DAYS', 7))
RECENT_ISSUE_DAYS=int(os.environ.get('W2_RECENT_ISSUE_DAYS', 7))

## Database configuration
DATABASE_ENGINE=os.environ.get('W2_DATABASE_ENGINE', 'django.db.backends.mysql')
DATABASE_HOST=os.environ.get('W2_DATABASE_HOST', '127.0.0.1')
DATABASE_NAME=os.environ.get('W2_DATABASE_NAME', 'wasa2il')
DATABASE_PASSWORD=os.environ.get('W2_DATABASE_PASSWORD', 'wasa2il')
DATABASE_PORT=os.environ.get('W2_DATABASE_PORT', '3306')
DATABASE_USER=os.environ.get('W2_DATABASE_USER', 'wasa2il')
DATABASE_EXPORT_DB_NAME=os.environ.get('W2_DATABASE_EXPORT_DB_NAME', '')

## Locale settings
DATETIME_FORMAT=os.environ.get('W2_DATETIME_FORMAT', 'd/m/Y H:i:s')
DATETIME_FORMAT_DJANGO_WIDGET=os.environ.get('W2_DATETIME_FORMAT_DJANGO_WIDGET', 'dd/mm/yyyy hh:ii')
DATE_FORMAT=os.environ.get('W2_DATE_FORMAT', 'd/m/Y')
LANGUAGE_CODE=os.environ.get('W2_LANGUAGE_CODE', 'en-US')
TIME_ZONE=os.environ.get('W2_TIME_ZONE', 'Iceland')
DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M:%S.%f',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d',
    '%d/%m/%Y %H:%M:%S',
    '%d/%m/%Y %H:%M:%S.%f',
    '%d/%m/%Y %H:%M',
    '%d/%m/%Y',
    '%d/%m/%y %H:%M:%S',
    '%d/%m/%y %H:%M:%S.%f',
    '%d/%m/%y %H:%M',
    '%d/%m/%y'
)

## Email settings
EMAIL_BACKEND=os.environ.get('W2_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
SERVER_EMAIL=os.environ.get('W2_SERVER_EMAIL', '')
DEFAULT_FROM_EMAIL=os.environ.get('W2_DEFAULT_FROM_EMAIL', '')
EMAIL_HOST = os.environ.get('W2_EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('W2_EMAIL_PORT', 25))
EMAIL_USE_TLS = os.environ.get('W2_EMAIL_USE_TLS', False) == '1'
EMAIL_USE_SSL = os.environ.get('W2_EMAIL_USE_SSL', False) == '1'
EMAIL_HOST_USER = os.environ.get('W2_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('W2_EMAIL_HOST_PASSWORD', '')
EMAIL_SUBJECT_PREFIX = os.environ.get('W2_EMAIL_SUBJECT_PREFIX', '[Wasa2il] ')

## Push notifications
GCM_APP_ID=os.environ.get('W2_GCM_APP_ID', '')
GCM_SENDER_ID=os.environ.get('W2_GCM_SENDER_ID', 0)
GCM_REST_API_KEY=os.environ.get('W2_GCM_REST_API_KEY', '')

## Facebook integration
INSTANCE_FACEBOOK_APP_ID=os.environ.get('W2_INSTANCE_FACEBOOK_APP_ID', '')
INSTANCE_FACEBOOK_IMAGE=os.environ.get('W2_INSTANCE_FACEBOOK_IMAGE', 'https://example.com/full/url/to/image.png')

## Discourse integration
DISCOURSE_URL=os.environ.get('W2_DISCOURSE_URL', '')
DISCOURSE_SECRET=os.environ.get('W2_DISCOURSE_SECRET', '')

## IcePirate integration
ICEPIRATE = {
    'url': os.environ.get('W2_ICEPIRATE_URL', ''),
    'key': os.environ.get('W2_ICEPIRATE_KEY', '')
}

# SAML (2.0) support
SAML = {
    'URL': os.environ.get('W2_SAML_URL', ''),
    'CERT': os.environ.get('W2_SAML_CERT', '')
}

FEATURES = {
    'tasks': os.environ.get('W2_FEATURE_TASKS', False) == '1',
    'topic': os.environ.get('W2_FEATURE_TOPIC', False) == '1',
    'push_notifications': os.environ.get('W2_FEATURE_PUSH_NOTIFICATIONS', False) == '1',
}

if not GCM_APP_ID:  # We cannot have push notifications without a registered app ID.
    FEATURES['push_notifications'] = False

# Get Wasa2il version.
with open(os.path.join(BASE_DIR, 'VERSION'), 'r') as f:
    WASA2IL_VERSION = f.readlines().pop(0).strip()
    h = sha256()
    h.update(("%s:%s" % (WASA2IL_VERSION, datetime.now())).encode('utf-8'))
    WASA2IL_HASH = h.hexdigest()[:7]


# Some error checking for local_settings
if not SECRET_KEY:
    raise Exception('You need to specify Django SECRET_KEY in the local_settings!')



MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DATABASE_NAME,                      # Or path to database file if using sqlite3.
        'USER': DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': DATABASE_PASSWORD,                  # Not used with sqlite3.
        'HOST': DATABASE_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': DATABASE_PORT,                      # Set to empty string for default. Not used with sqlite3.
    }
}

if DATABASE_EXPORT_DB_NAME:
    DATABASES['export'] = {
        'ENGINE': DATABASE_ENGINE,
        'NAME': '%s_export' % DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
        'OPTIONS': {
            'sql_mode': 'traditional',
        },
    }

# Deal with MySQL weirdness.
if DATABASE_ENGINE == 'django.db.backends.mysql':
    if not 'OPTIONS' in DATABASES['default']:
        DATABASES['default']['OPTIONS'] = {}
    DATABASES['default']['OPTIONS']['sql_mode'] = 'STRICT_TRANS_TABLES'

try:
    # Check for env var $DATABASE_URL (for Heroku)
    db_url = os.environ['DATABASE_URL']
    # If exists, confic accordingly
    import dj_database_url
    # Update database configuration with $DATABASE_URL.
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)
except KeyError:
    pass

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = (
  ('is', 'Íslenska'),
  ('en', 'English'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = here('uploads/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = here('static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)



MIDDLEWARE = (
    'cookiesdirective.middleware.CookiesDirectiveMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'languagecontrol.middleware.LanguageControlMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'core.middleware.AutoLogoutMiddleware',
    'termsandconditions.middleware.TermsAndConditionsRedirectMiddleware',
    'core.middleware.SamlMiddleware',
    'core.middleware.GlobalsMiddleware',
)
try:
    MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE_CLASSES
except:
    pass

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [here('templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'core.contextprocessors.auto_logged_out',
                'core.contextprocessors.globals',
                'polity.contextprocessors.navigation',
            ],
        },
    }
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


LOCALE_PATHS = (
    here('locale'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',

    'django.contrib.admin',

    'registration',
    'bootstrapform',
    'diff_match_patch',
    'datetimewidget',
    'crispy_forms',
    'termsandconditions',

    'languagecontrol',
    'emailconfirmation',

    'core',
    'polity',
    'topic',
    'election',
    'issue',
    'tasks',
    'gateway',
)
try:
    INSTALLED_APPS += LOCAL_INSTALLED_APPS
except:
    pass

CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

# Allow users to attempt log-ins using any of the following:
# e-mail address, SSN or username.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'core.authentication.SSNAuthenticationBackend',
#
# Note: It may make sense to disable the following, so merely compromising
# an e-mail account isn't sufficient to take over a wasa2il account. However,
# Icelandic SSNs are such poorly kept secrets (they're effectively public)
# that this wouldn't improve security for us, it'd just hurt usability.
#
    'core.authentication.EmailAuthenticationBackend',
)


# See http://docs.djangoproject.com/en/dev/topics/logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


TERMS_EXCLUDE_URL_PREFIX_LIST = (
    '/admin/',
    '/help/',
    '/accounts/register/',
    '/accounts/login/',
    '/accounts/logout/',
    '/accounts/verify/',
)

SAML_VERIFICATION_EXCLUDE_URL_PREFIX_LIST = (
    '/terms/',
)

AUTH_PROFILE_MODULE = "core.UserProfile"
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = "/"

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

if DEBUG:
    import imp
    try:
        imp.find_module('debug_toolbar')

        INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)
        MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
        INTERNAL_IPS = ('127.0.0.1',)
        DEBUG_TOOLBAR_CONFIG = {
            'JQUERY_URL': ''
        }
    except ImportError:
        # Silently continue if django-debug-toolbar isn't installed
        pass

if DEBUG:
    print("============ Wasa2il Features ============")
    for feature, enabled in FEATURES.items():
        print(" - %-25s      %8s" % (feature, ["DISABLED", "ENABLED"][enabled]))
    print("==========================================")
