#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals


import logging
log = logging.getLogger(__name__)

from decimal import Decimal as D

from django.db.models import get_model
from django.conf import settings
from oscar.apps.shipping.base import Base
from apps.shipping.utils import estimateWeight


SourceType = get_model('payment', 'SourceType')


class RusPost(Base):
    code = 'russian-post'
    name = "Почта России"
    is_tax_known = True
    is_sufficient = True
    defaultCharge = D(300)
    description = ("Доставка осуществляется Почтой России ценной бандеролью"
                   " либо посылкой")

    def set_shipping_addr(self, shipping_addr):
        self.set_postcode(shipping_addr)

    def set_postcode(self, shipping_address):
        log.debug("setting postcode")
        if shipping_address is not None:
            self.postcode = shipping_address.postcode

    @property
    def charge_incl_tax(self):
        log.debug("counting charge for RusPost")
        try:
            from tarifcalc import tarifcalc
        except ImportError:
            log.warning("tarifcalc not found!")
            return self.defaultCharge
        log.debug("tarifcalc found...")

        tarifRequest = dict(
            Weight=estimateWeight(self.basket),
            Valuation=self.basket.total_incl_tax_excl_discounts
        )

        from django.conf import settings
        try:
            tmppath = settings.TEMP
        except AttributeError:
            tmppath = settings.PROJECTPATH

        tarifConfig = {'zonesdbcfg': dict(
            DBPATH=settings.PROJECTPATH,
            TMPPATH=tmppath
        )}

	if hasattr(settings, 'TARIFCALC_TARIF'):
		tarifConfig.update(settings.TARIFCALC_TARIF)

        if hasattr(self, 'postcode'):
            tarifRequest['To'] = self.postcode
        log.debug("tarifRequest is %s", tarifRequest)
        try:
            charge = tarifcalc.calc(tarifRequest, tarifConfig)()
        except tarifcalc.BadTarifRequest as e:
            log.warning("Error getting RusPost charge: %s", e)
            return self.defaultCharge
        log.debug("completed: charge = %s", charge)
        return charge if charge else self.defaultCharge

    @property
    def charge_excl_tax(self):
        return self.basket_charge_incl_tax()

    @property
    def payment_methods_allowed(self):
        methods_allowed = SourceType.objects.exclude(
            name__iexact=settings.CASH_SOURCE_TYPE_NAME)
        log.debug("returning %s payment_methods", len(methods_allowed))
        return methods_allowed
