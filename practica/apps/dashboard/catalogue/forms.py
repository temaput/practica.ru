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
        exclude = ('display_order',)
    
    def save(self, *args, **kwargs):
        # We infer the display order of the image based on the order of the
        # image fields within the formset.
        kwargs['commit'] = False
        obj = super(ProductFragmentForm, self).save(*args, **kwargs)
        obj.display_order = self.get_display_order()
        obj.save()
        return obj

    def get_display_order(self):
        return self.prefix.split('-').pop()

BaseProductFragmentFormSet = inlineformset_factory(
    Product, ProductFragment, form=ProductFragmentForm, extra=2)

class ProductFragmentFormSet(BaseProductFragmentFormSet):
    def __init__(self, product_class, user, *args, **kwargs):
        super(ProductFragmentFormSet, self).__init__(*args, **kwargs)
