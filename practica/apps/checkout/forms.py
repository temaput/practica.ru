# set encoding=utf-8
from django.db.models import get_model
from oscar.apps.checkout import forms


class ShippingAddressForm(forms.ShippingAddressForm):

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        self.fields['line1'].label = u"Улица"
        self.fields['line2'].label = u"Дом, корпус, квартира, офис"

    class Meta:
        model = get_model('order', 'shippingaddress')
        fields = ('first_name', 'last_name', 'line4', 'line1', 'line2', 
                'postcode', 'phone_number', 'notes', 'country')
