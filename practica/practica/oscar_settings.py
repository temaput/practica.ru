#set encoding=utf-8

# Meta
# ====

OSCAR_SHOP_NAME = u'Издательский дом Практика'
OSCAR_SHOP_TAGLINE = u'Медицинская литература'
OSCAR_DEFAULT_CURRENCY = u'руб.' 
OSCAR_CURRENCY_LOCALE = 'ru_RU'
OSCAR_CURRENCY_FORMAT = u'#,##0.00 ¤'


OSCAR_ALLOW_ANON_CHECKOUT = True
OSCAR_ALLOW_ANON_REVIEWS = False
OSCAR_MODERATE_REVIEWS = True
OSCAR_FROM_EMAIL = 'order@granatbooks.ru'
OSCAR_STATIC_BASE_URL = 'granatbooks.ru'
from oscar.defaults import OSCAR_REQUIRED_ADDRESS_FIELDS
OSCAR_REQUIRED_ADDRESS_FIELDS += ('phone_number',)
