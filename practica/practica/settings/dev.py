from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = root('media')

#
# Debug toolbar
#
DEBUG_TOOLBAR_PATCH_SETTINGS = False
# INSTALLED_APPS += ('debug_toolbar',)
# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = ['127.0.0.1', 'localhost', '0.0.0.0']
DEBUG_TOOLBAR_CONFIG = {
}

YANDEX_METRIKA_ID = get_env('PRACTICA_YANDEX_METRIKA_ID')

# Logging
# =======

ERROR_TEST = True  #this should be false after succesfull testing
COMPRESS_ROOT = root('staticfiles')

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
    'filters': {  # describe additional conditions of logging
        'require_debug_false': {  # works only in production (for emailing to admins)
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {  # describe the destination of log (file, console, email...)
        'null': {  # do nothing
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {  # print to console
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'checkout_file': {  # all oscar logs printed to LOG_ROOT/filename
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
        'mail_admins': {  # this is for mailing admins in case of any ERROR
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'root': {  # all other loggers
        'handlers': ['console'],
        'level': 'DEBUG',
        },
    'loggers': {  # the are the loggers that correspond to getLogger(name)
        'django': {  # correspond to getLogger('django')
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {  # getLogger('django.request')
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
            'handlers':['console'],
            'propagate': False,
            'level': 'DEBUG'
            },
        'tarifcalc': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO'
            },
        'catalogue': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG'
            },
        # suppress output of this debug toolbar panel
        'template_timings_panel': {  # this has something to do with django debug panel
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
