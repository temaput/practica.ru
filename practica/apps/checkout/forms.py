# set encoding=utf-8
from django.db.models import get_model
from django.utils.translation import ugettext as _
from oscar.apps.checkout import forms as core_forms
from django import forms


class S:
    pass
settings = S()
settings.DEFAULT_POSTCODE = "000000"


class ShippingAddressForm(core_forms.ShippingAddressForm):
    username = forms.EmailField(label=_("My email address is"))

    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop('exclude_fields', ())
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        self.exclude_fields(exclude_fields)

    def exclude_fields(self, exclude_fields):
        for fname in exclude_fields:
            self.fields.pop(fname, None)

    def clean(self):
        if not len(self.instance.postcode):
            self.instance.postcode = settings.DEFAULT_POSTCODE
        return super(ShippingAddressForm, self).clean()

    class Meta:
        model = get_model('order', 'shippingaddress')
        fields = ('first_name', 'last_name', 'line4', 'line1', 'line2',
                  'line3', 'postcode', 'phone_number', 'notes', 'country')
