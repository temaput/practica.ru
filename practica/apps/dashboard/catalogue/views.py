from oscar.apps.dashboard.catalogue.views \
        import ProductCreateUpdateView as CoreProductCreateUpdateView

from forms import ProductForm, ProductFragmentFormSet

class ProductCreateUpdateView(CoreProductCreateUpdateView):
    form_class = ProductForm
    fragment_formset = ProductFragmentFormSet




