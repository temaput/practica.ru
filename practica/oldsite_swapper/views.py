from django.db.models import get_model
from django.http import Http404

from logging import getLogger
log = getLogger('oldsite_swapper.views')

Product = get_model('catalogue', 'Product')

from django.views.generic.base import RedirectView


class OldSiteSwapper(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        log.debug("in get_redirect_url")

        oldsite_product = Product.objects.filter(
            attribute_values__value_text__iexact=kwargs['old_href']
        )
        if oldsite_product.exists():
            return oldsite_product.first().get_absolute_url()
        else:
            raise Http404



# Create your views here.
