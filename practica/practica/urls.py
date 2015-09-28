
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.db.models import get_model
from oscar.views import handler500, handler404, handler403

from app import application

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

Product = get_model('catalogue', 'Product')
products = {'queryset': Product.objects.all()}
sitemaps = {
            'flatpages': FlatPageSitemap,
            'products': GenericSitemap(products, priority=1.0),
                }

urlpatterns = patterns('',

    # Examples:
        # url(r'^$', RedirectView.as_view(url='/catalogue'), name='home'),
        url(r'', include(application.urls)),
    # url(r'^granatshop/', include('granatshop.foo.urls')),

    # Robokassa integration...
    # (r'^checkout/robokassa/', include('robokassa.urls')),

    # sitemap.xml
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    # Uncomment the admin/doc line below to enable admin documentation:
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
        url(r'^admin/', include(admin.site.urls)),
    # favicon for every page
	url(r'^favicon\.ico$', RedirectView.as_view(url='/static/oscar/favicon.ico')),
    # old index page
	url(r'^index\.htm$', RedirectView.as_view(url='/')),

)

# Install Silk profiler
# urlpatterns += patterns('',
#                         url(r'^silk', include('silk.urls', namespace='silk')))
# Allow rosetta to be used to add translations
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^rosetta/', include('rosetta.urls')),
    )

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

    # Server statics and uploaded media
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # Allow error pages to be tested
    urlpatterns += patterns('',
        url(r'^403$', handler403),
        url(r'^404$', handler404),
        url(r'^500$', handler500)
    )
if settings.ERROR_TEST:
    # We add some bullshit address just to check that errors are reported
    urlpatterns += patterns('',
            url(r'^500errortest$','practica.error_test.raise_error')
            )
