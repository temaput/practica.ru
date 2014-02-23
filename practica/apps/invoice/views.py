#set encoding=utf-8
# Create your views here.

from django.views.generic import View 
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse, Http404
from django.db.models import get_model

from drawinvoice import sbrfslip, simpleinvoice

Order = get_model('order', 'Order')

class InvoiceContextMixin(SingleObjectMixin):

    model = Order
    pk_url_kwarg = 'order_pk'

    def parse_order(self):
        order = self.get_object()
        verification_hash = self.request.GET.get('hash', None)
        if verification_hash != order.verification_hash():
            raise Http404

        if order.is_anonymous:
            username = order.shipping_address.name
        else:
            username = order.user.get_full_name()
        self.customer =  dict(
                name = username,
                address = order.shipping_address.join_fields(
                    ('postcode', 'city', 'line1', 'line2', 'line3'), u', ')
                )

        from django.conf import settings
        self.beneficiary = getattr(settings, 'REQUISITES', {})
        self.goods = (dict(
                    name = item.product.title,
                    quantity = item.quantity,
                    amount = item.line_price_incl_tax,
                    tax = item.line_price_tax) for item in order.lines.all())
        # Here we hardcode shipping into goods in case it is not free

        if order.shipping_incl_tax:
            self.goods = tuple(self.goods) + (dict(
                name = u'Доставка',
                quantity = 1,
                amount = order.shipping_incl_tax,
                tax = order.shipping_tax),)

        self.order = dict(
                amount = order.total_incl_tax,
                tax = order.total_tax,
                paymentName = u'Оплата заказа №{}'.format(order.number),
                no = order.number
                )


class SbrfSlipView(View, InvoiceContextMixin):

    def get(self, request, *args, **kwargs):
        self.parse_order()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sbrfslip.pdf"'
        slip = sbrfslip.SbrfSlip(response)
        slip.feed(customer=self.customer,
                beneficiary=self.beneficiary,
                order=self.order)
        slip.write()

        return response


class SimpleInvoiceView(View, InvoiceContextMixin):
    def get(self, request, *args, **kwargs):
        self.parse_order()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="invoice.pdf"'
        slip = simpleinvoice.Invoice(response)
        slip.feed(customer=self.customer,
                beneficiary=self.beneficiary,
                goods=self.goods)
        slip.write()

        return response
