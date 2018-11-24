#coding:utf-8
# Django settings for wasa2il project.

import os
from utils import here
from datetime import datetime
from hashlib import sha256

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from local_settings import *
except ImportError:
    from default_settings import *
    print('No local_settings.py found. Setting default values.')

# Get Wasa2il version.
with open(os.path.join(BASE_DIR, 'VERSION'), 'r') as f:
    WASA2IL_VERSION = f.readlines().pop(0).strip()
    h = sha256()
    h.update("%s:%s" % (WASA2IL_VERSION, datetime.now()))
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
USE_L10N = True

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



MIDDLEWARE_CLASSES = (
    'cookiesdirective.middleware.CookiesDirectiveMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'languagecontrol.middleware.LanguageControlMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'core.middleware.GlobalsMiddleware',
    'core.middleware.AutoLogoutMiddleware',
    'core.middleware.CustomTermsAndConditionsRedirectMiddleware',
    'core.middleware.SamlMiddleware',
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
                'core.contextprocessors.globals',
                'core.contextprocessors.auto_logged_out',
                'polity.contextprocessors.polities',
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

    'sslserver',

    'registration',
    'bootstrapform',
    'diff_match_patch',
    'datetimewidget',
    'crispy_forms',
    'prosemirror',
    'termsandconditions',

    'languagecontrol',

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

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
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
