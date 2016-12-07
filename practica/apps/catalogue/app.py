from django.conf.urls import patterns, url
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import get_model

from oscar.apps.catalogue.app import ReviewsApplication
from oscar.apps.catalogue.app import BaseCatalogueApplication as CoreCatApp
from practica.cache_utils import invalidate_template_cache
from . import views


class BaseCatalogueApplication(CoreCatApp):
    detail_ajah = views.ProductDetailAjah
    category_view = views.ProductCategoryView

    def get_urls(self):
        urlpatterns = super(BaseCatalogueApplication, self).get_urls()
        urls = [
            # has different urlname for legacy reasons
            url(r'^$', self.category_view.as_view(), name='index'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.detail_view.as_view(), name='detail'),
            url(r'^ajah/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.detail_ajah.as_view(), name='detail_ajah'),
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
                self.category_view.as_view(), name='category'),
            # fallback URL if a user chops of the last part of the URL
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)/$',
                self.category_view.as_view()),
            url(r'^ranges/(?P<slug>[\w-]+)/$',
                self.range_view.as_view(), name='range')]
        urlpatterns += patterns('', *urls)
        return self.post_process_urls(urlpatterns)


class CatalogueApplication(BaseCatalogueApplication, ReviewsApplication):
    """
    Composite class combining Products with Reviews
    """


application = CatalogueApplication()

MODELS = (
    ('catalogue', 'Product'),
    ('catalogue', 'ProductCategory'),
)
MODELS_LIST = tuple(
    get_model(app, modelname) for app, modelname in MODELS
)


@receiver(post_save)
def invalidate_cache(sender, **kwargs):
    if sender in MODELS_LIST:
        invalidate_template_cache()
