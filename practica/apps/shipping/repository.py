#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from logging import getLogger
log = getLogger("shipping.repository")


from oscar.apps.shipping import repository
from apps.shipping.methods import (
    RusPost,)
from apps.shipping.models import (
    FixedPriceShipping,)
from oscar.apps.shipping.methods import NoShippingRequired


class Repository(repository.Repository):
    methods = (FixedPriceShipping, RusPost)

    def group_methods(self):
        methods = []
        self.preliminary_methods = []
        self.sufficient_methods = []
        self.methods_dict = {}
        for m in self.methods:
            if hasattr(m, 'objects'):
                for mm in m.objects.all():
                    methods.append(mm)
            else:
                methods.append(m())
        for m in methods:
            self.methods_dict[m.code] = m
            if getattr(m, 'is_shortcut', False):
                self.preliminary_methods.append(m)
            if getattr(m, 'is_sufficient', False):
                self.sufficient_methods.append(m)
        self.all_methods = methods
        self.final_methods = \
            list(set(methods) - set(self.preliminary_methods))

    def inject_address(self, shipping_addr):
        for m in self.sufficient_methods[:]:
            log.debug("injecting addres in method %s", m)
            if hasattr(m, 'approve_address'):
                if not m.approve_address(shipping_addr):
                    log.debug("address not approved")
                    self.sufficient_methods.remove(m)
                    if m in self.final_methods:
                        self.final_methods.remove(m)
                    continue
            log.debug("address is ok")
            if hasattr(m, 'set_shipping_addr'):
                m.set_shipping_addr(shipping_addr)

    def prepare_methods(self, basket, shipping_addr, **kwargs):
        self.group_methods()
        if shipping_addr is not None:
            self.inject_address(shipping_addr)

    def get_shipping_methods(self, user, basket, shipping_addr=None,
                             request=None, **kwargs):
        """
        Return a list of all applicable shipping method objects
        for a given basket, address etc.

        """
        if not basket.is_shipping_required():
            return [NoShippingRequired()]
        # We need to instantiate each method class to avoid thread-safety
        # issues
        self.prepare_methods(basket, shipping_addr, **kwargs)
        # 1. return preliminary methods
        if 'preliminary' in kwargs:
            return self.prime_methods(basket, self.preliminary_methods)
        # 3. return final (not preliminary) methods
        if 'preliminary_code' in kwargs:
            method = self.methods_dict.get(
                kwargs['preliminary_code'], None)
            if method is not None:
                if method in self.sufficient_methods:
                    return (self.prime_method(basket, method),)
                else:
                    if len(self.final_methods):
                        return self.prime_methods(basket, self.final_methods)
        # 2. return sufficient methods (default)
        return self.prime_methods(basket, self.sufficient_methods)

    def find_by_code(self, code, basket, shipping_addr=None):
        """
        Return the appropriate Method object for the given code
        """
        self.prepare_methods(basket, shipping_addr)
        # Check for NoShippingRequired as that is a special case
        if not code in self.methods_dict or code == NoShippingRequired.code:
            return self.prime_method(basket, NoShippingRequired())
        return self.prime_method(basket, self.methods_dict[code])
