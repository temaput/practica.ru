#set encoding=utf-8

import logging
log = logging.getLogger(__name__)

from decimal import Decimal as D

from django.utils.translation import ugettext_lazy as _
from oscar.apps.shipping.base import Base
from oscar.apps.shipping.methods import Free
from apps.shipping.utils import estimateWeight


class Pickup(Free):
    """
    Customer pick-up (самовывоз)
    """
    code = "customer-pick-up"
    name = u"Самовывоз"


class Express(Base):
    code = 'express-delivery-shipping'
    name = u"Курьер"
    is_tax_known = True
    charge_incl_tax = charge_excl_tax = D(300)



class RusPost(Base):
    code = 'russian-post'
    name = u"Почта России"
    is_tax_known = True
    defaultCharge = D(300)
    

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
            Weight = estimateWeight(self.basket),
            Valuation = self.basket.total_incl_tax_excl_discounts
            )

        from django.conf import settings
        try:
            tmppath = settings.TEMP
        except AttributeError:
            tmppath = settings.PROJECTPATH

        tarifConfig = {'zonesdbcfg': dict(
            DBPATH = settings.PROJECTPATH,
            TMPPATH = tmppath
            )}
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


