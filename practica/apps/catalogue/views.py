from oscar.apps.catalogue.views import ProductDetailView

class ProductDetailAjah(ProductDetailView):
    enforce_paths = False

    def get_template_names(self):
        return [
            '%s/detail_ajah.html' % (self.template_folder)]
