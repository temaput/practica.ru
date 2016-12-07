from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

CACHE_KEYS = (
    'home_products',
    'home_carousel',
)


def invalidate_template_cache():
    for k in CACHE_KEYS:
        key = make_template_fragment_key(k)
        cache.delete(key)
