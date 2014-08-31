from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect

from oscar.apps.dashboard.catalogue.views \
        import ProductCreateUpdateView as CoreProductCreateUpdateView

from forms import ProductForm, ProductFragmentFormSet

class ProductCreateUpdateView(CoreProductCreateUpdateView):
    form_class = ProductForm
    fragment_formset = ProductFragmentFormSet

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreateUpdateView, self).get_context_data(**kwargs)
        if 'fragment_formset' not in ctx:
            ctx['fragment_formset'] \
                = self.fragment_formset(instance=self.object)
        return ctx



    def process_all_forms(self, form):
        """
        Short-circuits the regular logic to have one place to have our
        logic to check all forms
        """
        # Need to create the product here because the inline forms need it
        # can't use commit=False because ProductForm does not support it
        if self.creating and form.is_valid():
            self.object = form.save()

        stockrecord_formset = self.stockrecord_formset(
            self.product_class, self.request.user,
            self.request.POST, instance=self.object)
        category_formset = self.category_formset(
            self.request.POST, instance=self.object)
        fragment_formset = self.fragment_formset(
            self.request.POST, self.request.FILES, instance=self.object)
        image_formset = self.image_formset(
            self.request.POST, self.request.FILES, instance=self.object)
        recommended_formset = self.recommendations_formset(
            self.request.POST, self.request.FILES, instance=self.object)

        is_valid = all([
            form.is_valid(),
            category_formset.is_valid(),
            fragment_formset.is_valid(),
            image_formset.is_valid(),
            recommended_formset.is_valid(),
            stockrecord_formset.is_valid(),
        ])

        if is_valid:
            return self.forms_valid(
                form, stockrecord_formset, category_formset,
                fragment_formset, image_formset, recommended_formset)
        else:
            # delete the temporary product again
            if self.creating and form.is_valid():
                self.object.delete()
                self.object = None
            # We currently don't hold on to images if the other formsets didn't
            # validate. But as the browser won't re-POST any images, we can do
            # no better than re-bind the image formset, which means the user
            # will have to re-select the images (see #1126)
            image_formset = self.image_formset(instance=self.object)

            return self.forms_invalid(
                form, stockrecord_formset, category_formset,
                fragment_formset, image_formset, recommended_formset)

    def forms_valid(self, form, stockrecord_formset, category_formset,
                    fragment_formset, image_formset, recommended_formset):
        """
        Save all changes and display a success url.
        """
        if not self.creating:
            # a just created product was already saved in process_all_forms()
            self.object = form.save()

        # Save formsets
        category_formset.save()
        fragment_formset.save()
        image_formset.save()
        recommended_formset.save()
        stockrecord_formset.save()

        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, stockrecord_formset, category_formset,
                      fragment_formset, image_formset, recommended_formset):
        messages.error(self.request,
                       _("Your submitted data was not valid - please "
                         "correct the below errors"))
        ctx = self.get_context_data(form=form,
                                    stockrecord_formset=stockrecord_formset,
                                    category_formset=category_formset,
                                    fragment_formset=fragment_formset,
                                    image_formset=image_formset,
                                    recommended_formset=recommended_formset)
        return self.render_to_response(ctx)
