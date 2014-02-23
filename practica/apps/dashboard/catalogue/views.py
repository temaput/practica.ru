import six
from oscar.apps.dashboard.catalogue.views \
        import ProductCreateUpdateView as CoreProductCreateUpdateView

from forms import ProductForm, ProductFragmentFormSet
from django.views import generic
from django.db.models import get_model
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.core.urlresolvers import reverse

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

from oscar.core.loading import get_classes

def filter_products(queryset, user):
    """
    Restrict the queryset to products the given user has access to.
    A staff user is allowed to access all Products.
    A non-staff user is only allowed access to a product if they are in at
    least one stock record's partner user list.
    """
    if user.is_staff:
        return queryset

    return queryset.filter(stockrecords__partner__users__pk=user.pk).distinct()

(ProductForm,
 ProductSearchForm,
 CategoryForm,
 StockRecordFormSet,
 StockAlertSearchForm,
 ProductCategoryFormSet,
 ProductImageFormSet,
 ProductRecommendationFormSet) \
    = get_classes('dashboard.catalogue.forms',
                  ('ProductForm',
                   'ProductSearchForm',
                   'CategoryForm',
                   'StockRecordFormSet',
                   'StockAlertSearchForm',
                   'ProductCategoryFormSet',
                   'ProductImageFormSet',
                   'ProductRecommendationFormSet'))
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductImage = get_model('catalogue', 'ProductImage')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductClass = get_model('catalogue', 'ProductClass')
StockRecord = get_model('partner', 'StockRecord')
StockAlert = get_model('partner', 'StockAlert')
Partner = get_model('partner', 'Partner')


class ProductCreateUpdateView(generic.UpdateView):
    """
    Dashboard view that bundles both creating and updating single products.
    Supports the permission-based dashboard.
    """

    template_name = 'dashboard/catalogue/product_update.html'
    model = Product
    context_object_name = 'product'

    form_class = ProductForm
    category_formset = ProductCategoryFormSet
    image_formset = ProductImageFormSet
    recommendations_formset = ProductRecommendationFormSet
    stockrecord_formset = StockRecordFormSet
    form_class = ProductForm
    fragment_formset = ProductFragmentFormSet


    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        self.formsets = {'category_formset': self.category_formset,
                         'image_formset': self.image_formset,
                         'recommended_formset': self.recommendations_formset,
                         'stockrecord_formset': self.stockrecord_formset}
        self.formsets['fragment_formset'] = self.fragment_formset

    def get_queryset(self):
        """
        Filter products that the user doesn't have permission to update
        """
        return filter_products(Product.objects.all(), self.request.user)

    def get_object(self, queryset=None):
        """
        This parts allows generic.UpdateView to handle creating products as
        well. The only distinction between an UpdateView and a CreateView
        is that self.object is None. We emulate this behavior.
        Additionally, self.product_class is set.
        """
        self.creating = not 'pk' in self.kwargs
        if self.creating:
            try:
                product_class_slug = self.kwargs.get('product_class_slug',
                                                     None)
                self.product_class = ProductClass.objects.get(
                    slug=product_class_slug)
            except ObjectDoesNotExist:
                raise Http404
            else:
                return None  # success
        else:
            product = super(ProductCreateUpdateView, self).get_object(queryset)
            self.product_class = product.product_class
            return product

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreateUpdateView, self).get_context_data(**kwargs)
        ctx['product_class'] = self.product_class

        for ctx_name, formset_class in six.iteritems(self.formsets):
            if ctx_name not in ctx:
                ctx[ctx_name] = formset_class(self.product_class,
                                              self.request.user,
                                              instance=self.object)

        if self.object is None:
            ctx['title'] = _('Create new %s product') % self.product_class.name
        else:
            ctx['title'] = ctx['product'].get_title()
        return ctx

    def get_form_kwargs(self):
        kwargs = super(ProductCreateUpdateView, self).get_form_kwargs()
        kwargs['product_class'] = self.product_class
        return kwargs

    def process_all_forms(self, form):
        """
        Short-circuits the regular logic to have one place to have our
        logic to check all forms
        """
        # Need to create the product here because the inline forms need it
        # can't use commit=False because ProductForm does not support it
        if self.creating and form.is_valid():
            self.object = form.save()

        formsets = {}
        for ctx_name, formset_class in six.iteritems(self.formsets):
            formsets[ctx_name] = formset_class(self.product_class,
                                               self.request.user,
                                               self.request.POST,
                                               self.request.FILES,
                                               instance=self.object)

        is_valid = form.is_valid() and all([formset.is_valid()
                                            for formset in formsets.values()])

        cross_form_validation_result = self.clean(form, formsets)
        if is_valid and cross_form_validation_result:
            return self.forms_valid(form, formsets)
        else:
            return self.forms_invalid(form, formsets)

    # form_valid and form_invalid are called depending on the validation result
    # of just the product form and redisplay the form respectively return a
    # redirect to the success URL. In both cases we need to check our formsets
    # as well, so both methods do the same. process_all_forms then calls
    # forms_valid or forms_invalid respectively, which do the redisplay or
    # redirect.
    form_valid = form_invalid = process_all_forms

    def clean(self, form, formsets):
        """
        Perform any cross-form/formset validation. If there are errors, attach
        errors to a form or a form field so that they are displayed to the user
        and return False. If everything is valid, return True. This method will
        be called regardless of whether the individual forms are valid.
        """
        return True

    def forms_valid(self, form, formsets):
        """
        Save all changes and display a success url.
        """
        if not self.creating:
            # a just created product was already saved in process_all_forms()
            self.object = form.save()

        # Save formsets
        for formset in formsets.values():
            formset.save()

        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, formsets):
        # delete the temporary product again
        if self.creating and self.object and self.object.pk is not None:
            self.object.delete()
            self.object = None

        messages.error(self.request,
                       _("Your submitted data was not valid - please "
                         "correct the errors below"))
        ctx = self.get_context_data(form=form, **formsets)
        return self.render_to_response(ctx)

    def get_url_with_querystring(self, url):
        url_parts = [url]
        if self.request.GET.urlencode():
            url_parts += [self.request.GET.urlencode()]
        return "?".join(url_parts)

    def get_success_url(self):
        msg = render_to_string(
            'dashboard/catalogue/messages/product_saved.html',
            {
                'product': self.object,
                'creating': self.creating,
            })
        messages.success(self.request, msg)
        url = reverse('dashboard:catalogue-product-list')
        if self.request.POST.get('action') == 'continue':
            url = reverse('dashboard:catalogue-product',
                          kwargs={"pk": self.object.id})
        return self.get_url_with_querystring(url)

