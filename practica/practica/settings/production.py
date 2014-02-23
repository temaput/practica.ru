from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

import os
DOMAIN = 'granatbooks.ru'
DOMAINPATH = os.path.join(
        os.path.expanduser('~'), 'domains/{domain}'.format(domain=DOMAIN))
ondomain = lambda x: os.path.join(DOMAINPATH, x)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'granat-site_granatshop',                      # Or path to database file if using sqlite3.
        'USER': '045535102_django',                      # Not used with sqlite3.
        'PASSWORD': get_env('PRACTICA_MYSQL_PASSWORD'),                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT =  ondomain('media')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ondomain('static')

# Dunno if it works, need checking
TEMP = '/tmp/mc-granat-site'
SEND_BROKEN_LINK_EMAILS = True


ALLOWED_HOSTS = ['.{}'.format(DOMAIN)]

#
# ANALITICS
# =========

GOOGLE_ANALYTICS_ID = get_env('PRACTICA_GOOGLE_ANALYTICS_ID')
YANDEX_METRIKA_ID = get_env('PRACTICA_YANDEX_METRIKA_ID')


# EMAILS
#========

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'granatshop.smtpssl_backend.EmailSSLBackend'
EMAIL_HOST = 'smtp.jino.ru'
EMAIL_HOST_USER = os.environ['PRACTICA_EMAIL']
EMAIL_HOST_PASSWORD = os.environ['PRACTICA_EMAIL_PASSWORD']
EMAIL_USE_TLS = True
EMAIL_PORT = '465'
SERVER_EMAIL = EMAIL_HOST_USER
ERROR_TEST = False  #this should be false after succesfull testing


# Logging
# =======

LOG_ROOT = root('logs')
# Ensure log root exists
if not os.path.exists(LOG_ROOT):
    os.mkdir(LOG_ROOT)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'checkout_file': {
            'level': 'INFO',
            'class': 'oscar.core.logging.handlers.EnvFileHandler',
            'filename': 'checkout.log',
            'formatter': 'verbose'
        },
        'gateway_file': {
            'level': 'INFO',
            'class': 'oscar.core.logging.handlers.EnvFileHandler',
            'filename': 'gateway.log',
            'formatter': 'simple'
        },
        'error_file': {
            'level': 'INFO',
            'class': 'oscar.core.logging.handlers.EnvFileHandler',
            'filename': 'errors.log',
            'formatter': 'verbose'
        },
        'sorl_file': {
            'level': 'INFO',
            'class': 'oscar.core.logging.handlers.EnvFileHandler',
            'filename': 'sorl.log',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'oscar.checkout': {
            'handlers': ['console', 'checkout_file'],
            'propagate': True,
            'level': 'INFO',
        },
        'gateway': {
            'handlers': ['gateway_file'],
            'propagate': True,
            'level': 'INFO',
        },
        'sorl.thumbnail': {
            'handlers': ['sorl_file'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'robokassa': {
            'handlers': ['mail_admins', 'error_file'],
            'level': 'ERROR',
            'propagate': False
            },
        # suppress output of this debug toolbar panel
        'template_timings_panel': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}


