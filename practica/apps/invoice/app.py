from django.conf.urls import patterns, url, include

from oscar.core.application import Application

from apps.invoice.views import SimpleInvoiceView, SbrfSlipView

class Invoice(Application):
    name = 'invoice'
    sbrf_view = SbrfSlipView
    invoice_view = SimpleInvoiceView

    def get_urls(self):
        urlpatterns = patterns('',
                url(r'sbrfslip/(?P<order_pk>\d+)/$', self.sbrf_view.as_view(),
                    name='sbrf_slip'),
                url(r'simpleinvoice/(?P<order_pk>\d+)/$', self.invoice_view.as_view(),
                    name='invoice_payment')
                )
        return urlpatterns

application = Invoice()
    
