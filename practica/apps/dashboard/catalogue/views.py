from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect

from oscar.apps.dashboard.catalogue.views \
        import ProductCreateUpdateView as CoreProductCreateUpdateView

from forms import ProductForm, ProductFragmentFormSet, ProductCategoryFormSet


class ProductCreateUpdateView(CoreProductCreateUpdateView):
    form_class = ProductForm
    fragment_formset = ProductFragmentFormSet
    category_formset = ProductCategoryFormSet

    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        self.formsets = {'category_formset': self.category_formset,
                         'image_formset': self.image_formset,
                         'recommended_formset': self.recommendations_formset,
                         'stockrecord_formset': self.stockrecord_formset,
                         #'fragment_formset': self.fragment_formset
                         }

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreateUpdateView, self).get_context_data(**kwargs)
        # if 'fragment_formset' not in ctx:
          #  ctx['fragment_formset'] \
          #      = self.fragment_formset(instance=self.object)
        return ctx
