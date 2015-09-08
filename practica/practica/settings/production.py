from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG


from .local_settings import DATABASES

STATIC_ROOT = '/var/nginx/STATIC_ROOT'
MEDIA_ROOT = '/var/nginx/MEDIA_ROOT'

# Dunno if it works, need checking
SEND_BROKEN_LINK_EMAILS = True


ALLOWED_HOSTS = ['*']

#
# ANALITICS
# =========

GOOGLE_ANALYTICS_ID = get_env('PRACTICA_GOOGLE_ANALYTICS_ID')
YANDEX_METRIKA_ID = get_env('PRACTICA_YANDEX_METRIKA_ID')

#
# Compression
#
USE_LESS = True
COMPRESS_OFFLINE = False
COMPRESS_ENABLED = True


# Caching
# =====
# RAM caching used by default. Lets use redis

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
MIDDLEWARE_CLASSES = ('django.middleware.cache.UpdateCacheMiddleware',) + MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES += ('django.middleware.cache.FetchFromCacheMiddleware',)
CACHE_MIDDLEWARE_SECONDS = 600  # default

# use redis for sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# use redis for thumbnail lookup (sorl)
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_REDIS_DB = 1  # redis provides up to 16 dbs by default

# EMAILS
#========

EMAIL_BACKEND = 'granatshop.smtpssl_backend.EmailSSLBackend'
EMAIL_HOST = 'smtp.jino.ru'
EMAIL_HOST_USER = os.environ['PRACTICA_EMAIL']
EMAIL_HOST_PASSWORD = os.environ['PRACTICA_EMAIL_PASSWORD']
EMAIL_USE_TLS = True
EMAIL_PORT = '465'
SERVER_EMAIL = EMAIL_HOST_USER
ERROR_TEST = False  #this should be false after succesfull testing


ROBOKASSA_TEST_MODE = True
# Logging
# =======

ERROR_TEST = True  #this should be false after succesfull testing
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
        'handlers': ['error_file'],
        'level': 'ERROR',
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
            'handlers': ['checkout_file'],
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
            'handlers':['null'],
            'propagate': False,
            'level': 'INFO'
            },
        'tarifcalc': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'INFO'
            },
        'catalogue': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'ERROR'
            },
        # suppress output of this debug toolbar panel
        'template_timings_panel': {  # this has something to do with django debug panel
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
