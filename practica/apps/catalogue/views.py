from oscar.apps.catalogue.views import ProductDetailView

class ProductDetailAjah(ProductDetailView):

    def get(self, request, **kwargs):
        """
        Ensures that the correct URL is used before rendering a response
        """
        print("in ProductAjah")
        self.object = self.get_object()

        response = super(ProductDetailView, self).get(request, **kwargs)
        return response

    def get_template_names(self):
        """
        Return a list of possible templates.

        We try 2 options before defaulting to catalogue/detail.html:
            1). detail-for-upc-<upc>.html
            2). detail-for-class-<classname>.html

        This allows alternative templates to be provided for a per-product
        and a per-item-class basis.
        """
        return [
            '%s/detail_ajah.html' % (self.template_folder)]
