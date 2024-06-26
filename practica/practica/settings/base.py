# Django settings for practica project.

import os
from os.path import join, realpath, pardir, dirname


from django.core.exceptions import ImproperlyConfigured

def get_env(name, fallback='not set'):
    try:
        val = os.environ[name]
        if val == 'False':
            return False
        if val == 'True':
            return True
        if val == '0':
            return 0
        if val == '1':
            return 1
        return val
    except KeyError:
        if fallback is not None:
            return fallback
        else:
            raise ImproperlyConfigured("%s env var not set" % name)

PROJECTPATH =  realpath(join(dirname(__file__), pardir, pardir))
root = lambda x: join(PROJECTPATH, x)

ADMINS = (
    ('Sergey Ananich', 's.ananich@mail.ru'),
)


MANAGERS = ADMINS


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

LANGUAGES = (
            ('ru', 'Russian'),
            )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'


# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
        root('static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'django_practica',                      # Or path to database file if using sqlite3.
        'USER': 'tema',                      # Not used with sqlite3.
        'PASSWORD': '1770Beethoven',                  # Not used with sqlite3.
        'HOST': 'db',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': 5432,                      # Set to empty string for default. Not used with sqlite3.
    }
}


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.

SECRET_KEY = get_env('DJANGO_SECRET_KEY', 'not set')

# ==============
# Robokassa settings
# ==============
ROBOKASSA_LOGIN = get_env("PRACTICA_ROBOKASSA_LOGIN", None)
ROBOKASSA_PASSWORD1 = get_env('PRACTICA_ROBOKASSA_PASSWORD1', None)
ROBOKASSA_PASSWORD2 = get_env('PRACTICA_ROBOKASSA_PASSWORD2', None)
ROBOKASSA_TEST_MODE = get_env('PRACTICA_ROBOKASSA_TEST_MODE', False)
ROBOKASSA_USE_POST = True
ROBOKASSA_STRICT_CHECK = get_env('PRACTICA_ROBOKASSA_STRICT_CHECK', False)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'middleware.AjaxMessaging',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.Emailbackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'oscar.apps.search.context_processors.search_form',
    'oscar.apps.promotions.context_processors.promotions',
    'oscar.apps.checkout.context_processors.checkout',
    'oscar.apps.customer.notifications.context_processors.notifications',
    'oscar.core.context_processors.metadata',
    'practica.context_processors.metadata',
)

ROOT_URLCONF = 'practica.urls'

# Python dotted path to the WSGI application used by Django's runserver.
# WSGI_APPLICATION = 'granatshop.wsgi.application'

from oscar import OSCAR_MAIN_TEMPLATE_DIR
TEMPLATE_DIRS = (
        root('templates'),
    OSCAR_MAIN_TEMPLATE_DIR,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)
COMPRESS_CSS_FILTERS = ('compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': '/data/whoosh_index'
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

from oscar import get_core_apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    'south',
    'compressor',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'haystack',
    'robokassa',
    'practica_templatetags',
] + get_core_apps(['apps.promotions', 'apps.basket', 'apps.checkout',
                   'apps.catalogue', 'apps.shipping', 'apps.payment',
                   'apps.order', 'apps.address'])


#LOCALE
#=======

LOCALE_PATHS = (root( 'locale'),)

# ==============
# Oscar settings
# ==============

from oscar.defaults import *
from practica.oscar_settings import *
from practica.requisites import REQUISITES
# from practica.robokassa_settings import *
from practica.practica_settings import *
from practica.tarifcalc_settings import *



