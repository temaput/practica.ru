from django.conf.urls import patterns, url, include

from oscar.app import Shop

from apps.checkout.app import application as checkout_app
from apps.invoice.app import application as invoice_app
from apps.dashboard.app import application as dashboard_app



class Main(Shop):
    # Use local checkout app so we can mess with the view classes
    checkout_app = checkout_app
    invoice_app = invoice_app
    dashboard_app = dashboard_app

    def get_urls(self):
        urlpatterns = super(Main, self).get_urls()
        urlpatterns += patterns('',
                url(r"^invoice/", include(self.invoice_app.urls))
                )

        return urlpatterns



application = Main()
