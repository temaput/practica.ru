from django.db.models import get_model
from django.forms.models import inlineformset_factory
from django import forms as django_forms
from oscar.apps.dashboard.catalogue import forms

ProductFragment = get_model('catalogue', 'ProductFragment')
Product = get_model('catalogue', 'Product')

class ProductForm(forms.ProductForm):

    class Meta(forms.ProductForm.Meta):
        fields = ('upc', 'title', 'authors', 'description', 'contents', 'slug', 
                  'related_products', 'parent', 'is_discountable')
        exclude = None

class ProductFragmentForm(django_forms.ModelForm):
    class Meta:
        model = ProductFragment

ProductFragmentFormSet = inlineformset_factory(
    Product, ProductFragment, form=ProductFragmentForm, extra=5)