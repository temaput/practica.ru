#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from logging import getLogger
log = getLogger("checkout.views")

#from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.db.models import get_model, get_models
from django.views.generic import TemplateView

from oscar.core.loading import get_class, get_classes
from oscar.core.compat import get_user_model


from oscar.apps.checkout import views as core_views
from oscar.apps.checkout.views import PaymentDetailsView \
    as corePaymentDetailsView

from oscar.apps.checkout.views import ThankYouView as coreThankYouView

from apps.shipping import models as shipping_models_module

RedirectRequired, UnableToTakePayment, PaymentError = get_classes(
    'payment.exceptions', ['RedirectRequired', 'UnableToTakePayment',
                           'PaymentError'])

Dispatcher = get_class('customer.utils', 'Dispatcher')
CommunicationEventType = get_model('customer', 'CommunicationEventType')
Order = get_model('order', 'Order')
SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')
CheckoutSessionData = get_class('checkout.utils', 'CheckoutSessionData')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
Repository = get_class('shipping.repository', 'Repository')
# defered payment codes - коды офлайновых способов оплаты,
# нал, через банк, по счету
DeferedPaymentCodes = ('cash_payment', 'sbrf_slip', 'invoice_payment')
RedirectPaymentCodes = ('robokassa',)
RemotePaymentCodes = ('sbrf_slip', 'invoice_payment', 'robokassa')

shipping_models = get_models(shipping_models_module)
User = get_user_model()


def get_shipping_method(method_code):
    for ShippingMethodModel in shipping_models:
        if ShippingMethodModel.objects.filter(code=method_code).exists():
            return ShippingMethodModel.objects.get(code=method_code)


class IndexView(CheckoutSessionMixin, TemplateView):
    """
    Just show index.html nothing else to be done here
    We will collect guest-email with other contact info
    """
    template_name = 'checkout/gateway.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['login_next'] = reverse('checkout:shipping-address')
        context['shipping_methods'] = Repository().get_shipping_methods(
            self.request.user, self.request.basket, preliminary=True)
        return context

    def post(self, request, *args, **kwargs):
        """
        We look for shipping_method in POST
        """
        # Need to check that this code is valid for this user
        method_code = request.POST.get('method_code', None)
        self.checkout_session.use_shipping_method(method_code)
        return self.get_success_response()

    def get_success_response(self):
        return HttpResponseRedirect(reverse('checkout:shipping-address'))


class ShippingAddressView(core_views.ShippingAddressView):
    pre_conditions = ('check_basket_is_not_empty',
                      'check_basket_is_valid',
                      'check_basket_requires_shipping')

    def get_form_kwargs(self):
        kwargs = super(ShippingAddressView, self).get_form_kwargs()
        exclude_fields = []
        if 'full' in self.request.GET:
            self.checkout_session.reset_shipping_data()
        if self.request.user.is_authenticated():
            exclude_fields.append('username')
        if self.checkout_session.is_shipping_method_set(self.request.basket):
            shipping_method = get_shipping_method(
                self.checkout_session.shipping_method_code(
                    self.request.basket))
            for fname in ('line4', 'line1', 'line2', 'line3',
                          'postcode', 'country'):
                if getattr(shipping_method, fname, None):
                    exclude_fields.append(fname)

        if len(exclude_fields):
            kwargs['exclude_fields'] = exclude_fields
        return kwargs

    def get_initial(self):
        initial = {}
        initial.update(
            self.checkout_session.new_shipping_address_fields() or {})
        if 'postcode' in initial:
            if initial['postcode'] == '000000':
                initial['postcode'] = ''
        initial['username'] = self.checkout_session.get_guest_email()
        return initial

    def form_invalid(self, form):
        log.debug("form errors: %s", form.errors)
        return super(ShippingAddressView, self).form_invalid(form)

    def form_valid(self, form):
        # Store the address details in the session and redirect to next step
        log.debug("form is valid")
        if not self.request.user.is_authenticated():
            email = form.cleaned_data.get('username', None)
            if email is not None:
                self.checkout_session.set_guest_email(email)
        address_fields = dict(
            (k, v) for (k, v) in form.instance.__dict__.items()
            if not k.startswith('_'))
        log.debug("address_fields is %s", address_fields)
        # Lets check for preliminary filled address fields
        if self.checkout_session.is_shipping_method_set(self.request.basket):
            default_values = {}
            shipping_method = get_shipping_method(
                self.checkout_session.shipping_method_code(
                    self.request.basket))
            for fname in ('line1', 'line2', 'line3', 'line4', 'postcode'):
                _val = getattr(shipping_method, fname, None)
                log.debug("setting %s to default: %s", fname, _val)
                if _val and not address_fields[fname]:
                    default_values[fname] = _val
            if default_values:
                log.debug("injecting default values %s into instance %s",
                          default_values, form.instance)
                address_fields.update(default_values)
                form.instance.__dict__.update(default_values)
        self.checkout_session.ship_to_new_address(address_fields)
        return super(ShippingAddressView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ShippingAddressView, self).get_context_data(**kwargs)
        context['login_next'] = reverse('checkout:shipping-address')
        return context


class ShippingMethodView(core_views.ShippingMethodView):

    def get_context_data(self, **kwargs):
        kwargs = super(ShippingMethodView, self).get_context_data(**kwargs)
        kwargs['shipping_methods'] = self._methods
        return kwargs

    def get_available_shipping_methods(self):
        """
        Returns all applicable shipping method objects
        for a given basket.
        """
        # Shipping methods can depend on the user, the contents of the basket
        # and the shipping address.  I haven't come across a scenario that
        # doesn't fit this system.
        if 'full' in self.request.GET:
            preliminary_code = None
        else:
            preliminary_code = self.checkout_session.shipping_method_code(
                self.request.basket)

        return Repository().get_shipping_methods(
            user=self.request.user, basket=self.request.basket,
            shipping_addr=self.get_shipping_address(self.request.basket),
            request=self.request,
            preliminary_code=preliminary_code)


class PaymentMethodView(CheckoutSessionMixin, TemplateView):
    template_name = 'checkout/payment_methods.html'
    pre_conditions = (
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_shipping_data_is_captured')

    def post(self, request, *args, **kwargs):
        method_code = request.POST.get('method_code', None)
        #Check the validity of method
        log.debug("Payment method code = %s", method_code)
        if method_code in [m.code for m in
                           self.get_available_payment_methods()]:
            self.checkout_session.pay_by(method_code)

        return self.get_success_response()

    def get_available_payment_methods(self):
        source_types = SourceType.objects.all()
        shipping_method = self.get_shipping_method(self.request.basket)
        return getattr(shipping_method,
                       'payment_methods_allowed', source_types)

    def get_context_data(self, **kwargs):
        ctx = super(PaymentMethodView, self).get_context_data(**kwargs)
        ctx['payment_methods'] = self.get_available_payment_methods()
        return ctx

    def get_success_response(self):
        return HttpResponseRedirect(reverse('checkout:preview'))


class PaymentDetailsView(corePaymentDetailsView):

    def get_context_data(self, **kwargs):
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['payment_method'] = self.checkout_session.payment_method()
        ctx.update(kwargs)
        return ctx

    def handle_payment(self, order_number, total, **kwargs):
        source_type = self.checkout_session.payment_method()
        log.debug("source_type code is %s", source_type.code)
        if not source_type.is_defered:
            log.debug("Not deferred")
            # here we parse the actual online payment
            if source_type.code in ("robokassa",):
                log.debug("Is robokassa")
                # we need to pass basket number and amount
                basket_num = self.checkout_session.get_submitted_basket_id()
                # this call supposed to raise RedirectRequiredError
                email = self.request.user.email if \
                    self.request.user.is_authenticated() else \
                    self.checkout_session.get_guest_email()
                try:
                    from robokassa.facade import robokassa_redirect
                    robokassa_redirect(
                        self.request, basket_num, total.incl_tax,
                        Email=email, Culture='ru', order_num=order_number)
                except ImportError:
                    pass
            raise UnableToTakePayment(u"Данный вид платежа не поддерживается")

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source = Source(source_type=source_type,
                        amount_allocated=total.incl_tax,
                        reference='')  # PA: reference could be No of invoice?
        self.add_payment_source(source)

        # Also record payment event
        self.add_payment_event(
            'pre-auth', total.incl_tax, reference='')


class ThankYouView(coreThankYouView):
    """
    Displays the 'thank you' page which summarises the order just submitted.
    """
    template_name = 'checkout/thank_you.html'
    context_object_name = 'order'

    def get_object(self):
        # We allow superusers to force an order thankyou page for testing
        order = None
        if self.request.user.is_superuser:
            if 'order_number' in self.request.GET:
                order = Order._default_manager.get(
                    number=self.request.GET['order_number'])
            elif 'order_id' in self.request.GET:
                order = Order._default_manager.get(
                    id=self.request.GET['order_id'])

        if not order:
            if 'checkout_order_id' in self.request.session:
                order = Order._default_manager.get(
                    pk=self.request.session['checkout_order_id'])
            else:
                raise Http404(_("No order found"))

        return order

    def get_context_data(self, **kwargs):
        ctx = super(ThankYouView, self).get_context_data(**kwargs)
        order = ctx.get("order", None)
        if order:
            payment_method = order.sources.all()[0].source_type
            if payment_method.code in ('sbrf_slip', 'invoice_payment'):
                ctx['print_invoice'] = True
                ctx['payment_method_code'] = payment_method.code
        return ctx
