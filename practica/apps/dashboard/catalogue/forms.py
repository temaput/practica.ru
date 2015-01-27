from django.db.models import get_model
from django.forms.models import inlineformset_factory
from django import forms as django_forms
from django.utils.translation import ugettext_lazy as _
from oscar.apps.dashboard.catalogue import forms

ProductFragment = get_model('catalogue', 'ProductFragment')
Product = get_model('catalogue', 'Product')
ProductCategory = get_model('catalogue', 'ProductCategory')

class ProductForm(forms.ProductForm):

    class Meta(forms.ProductForm.Meta):
        fields = ('upc', 'title', 'authors', 'description', 'contents', 'slug',
                  'related_products', 'parent', 'is_discountable')
        exclude = None

class ProductFragmentForm(django_forms.ModelForm):
    class Meta:
        model = ProductFragment

class ProductCategoryForm(django_forms.ModelForm):

    class Meta:
        model = ProductCategory
        fields = ('category', 'priority', )

BaseProductCategoryFormSet = inlineformset_factory(
    Product, ProductCategory, form=ProductCategoryForm, extra=3,
    can_delete=True)

BaseProductFragmentFormSet = inlineformset_factory(
    Product, ProductFragment, form=ProductFragmentForm, extra=5)

class ProductFragmentFormSet(BaseProductFragmentFormSet):
    def __init__(self, product_class, user, *args, **kwargs):
        super(ProductFragmentFormSet, self).__init__(*args, **kwargs)

class ProductCategoryFormSet(BaseProductCategoryFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        # This function just exists to drop the extra arguments
        super(ProductCategoryFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        if self.instance.is_top_level and self.get_num_categories() == 0:
            raise forms.ValidationError(
                _("A top-level product must have at least one category"))
        if self.instance.is_variant and self.get_num_categories() > 0:
            raise forms.ValidationError(
                _("A variant product should not have categories"))

    def get_num_categories(self):
        num_categories = 0
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if (hasattr(form, 'cleaned_data')
                    and form.cleaned_data.get('category', None)
                    and not form.cleaned_data.get('DELETE', False)):
                num_categories += 1
        return num_categories
