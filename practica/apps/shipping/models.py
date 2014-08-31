#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from decimal import Decimal as D
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import get_model
from oscar.models.fields import UppercaseCharField
from oscar.models.fields import AutoSlugField
PaymentMethod = get_model("payment", "SourceType")


class ShippingMethod(models.Model):
    # Fields from shipping.base.ShippingMethod must be added here manually.
    code = AutoSlugField(_("Slug"), max_length=128, unique=True,
                         populate_from='name')
    name = models.CharField(_("Name"), max_length=128, unique=True)
    description = models.TextField(_("Description"), blank=True)

    # We allow shipping methods to be linked to a specific set of countries
    countries = models.ManyToManyField('address.Country', null=True,
                                       blank=True, verbose_name=_("Countries"))

    is_discounted = False
    discount = D('0.00')
    _basket = None

    class Meta:
        abstract = True
        verbose_name = _("Shipping Method")
        verbose_name_plural = _("Shipping Methods")

    def __unicode__(self):
        return self.name

    def set_basket(self, basket):
        self._basket = basket


class GeneralShippingInfo(models.Model):

    line1 = models.CharField(_("First line of address"), max_length=255,
                             blank=True)
    line2 = models.CharField(
        _("Second line of address"), max_length=255, blank=True)
    line3 = models.CharField(
        _("Third line of address"), max_length=255, blank=True)
    line4 = models.CharField(_("City"), max_length=255, blank=True)
    postcode = UppercaseCharField(
        _("Post/Zip-code"), max_length=64, blank=True)
    is_shortcut = models.BooleanField(
        _("Show on preliminary form"), default=False)
    is_sufficient = models.BooleanField(
        _("Is self-sufficient method"), default=True,
        help_text=_("If this method was preliminary selected, do not "
                    "ask for method again after shipping address input"))
    allows_payment_methods = models.ManyToManyField(
        PaymentMethod, verbose_name=_("Payment methods allowed"), blank=True)
    upper_weight_limit = models.FloatField(_("Maximum weight allowed"),
                                           blank=True, null=True)
    # If basket value is above this threshold, then shipping is free
    free_shipping_threshold = models.DecimalField(
        _("Free Shipping"), decimal_places=2, max_digits=12, blank=True,
        null=True)

    @property
    def payment_methods_allowed(self):
        return self.allows_payment_methods.all()

    def approve_address(self, addr):
        #Check if address is compliant with this method (compare city name)
        city = addr.line4.lower().strip()
        if self.line4 and city != self.line4.lower().strip():
            return False
        return True

    class Meta:
        abstract = True


class FixedPriceShipping(ShippingMethod, GeneralShippingInfo):

    price_per_order = models.DecimalField(
        _("Price per order"), decimal_places=2, max_digits=12,
        default=D('0.00'))

    @property
    def charge_incl_tax(self):
        """
        Return basket total including tax
        """
        if self.free_shipping_threshold is not None and \
                self._basket.total_incl_tax >= self.free_shipping_threshold:
            return D('0.00')

        charge = self.price_per_order
        return charge

    @property
    def charge_excl_tax(self):
        """
        Return basket total excluding tax.

        Default implementation assumes shipping is tax free.
        """
        return self.charge_incl_tax

    @property
    def is_tax_known(self):
        # We assume tax is known
        return True

    class Meta:
        ordering = ('pk',)
