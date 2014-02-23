import os
from django.core.exceptions import ImproperlyConfigured

ROBOKASSA_LOGIN = r'granatbooks.ru'
try:
    ROBOKASSA_PASSWORD1 = os.environ['GRANAT_ROBOKASSA_PASSWORD1']
    ROBOKASSA_PASSWORD2 = os.environ['GRANAT_ROBOKASSA_PASSWORD2']
except KeyError:
    raise ImproperlyConfigured("Environment error: ROBOKASSA_PASSWORD")
ROBOKASSA_USE_POST = True
ROBOKASSA_STRICT_CHECK = True
ROBOKASSA_TEST_MODE = False
