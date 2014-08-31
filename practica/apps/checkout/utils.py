from oscar.apps.checkout.utils import CheckoutSessionData
from django.db.models import get_model
SourceType = get_model('payment', 'SourceType')


class CheckoutSessionData(CheckoutSessionData):

    # Payment methods
    # ===============

    def pay_by(self, code):
        self._set('payment', 'method_code', code)

    def payment_method(self):
        payment_code = self._get('payment', 'method_code')
        return SourceType.objects.get(code=payment_code)

    def ship_to_user_address(self, address):
        """
        Use an user address (from an address book) as the shipping address.
        """
        self._set('shipping', 'user_address_id', address.id)
