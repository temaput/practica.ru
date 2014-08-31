from django.conf.urls import patterns, url, include

from oscar.apps.catalogue.app import ReviewsApplication
from oscar.apps.catalogue.app import BaseCatalogueApplication as CoreCatApp
from . import views


class BaseCatalogueApplication(CoreCatApp):
    detail_ajah = views.ProductDetailAjah

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
