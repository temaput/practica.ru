from django.db.models import Min
from django.db.models import get_model
from oscar.apps.catalogue.views import ProductDetailView
from oscar.apps.catalogue.views import ProductCategoryView as \
    CoreProductCategoryView


Product = get_model("catalogue", "Product")


class ProductDetailAjah(ProductDetailView):
    enforce_paths = False

    def get_template_names(self):
        return [
            '%s/detail_ajah.html' % (self.template_folder)]


# Prioritize category lists
class ProductCategoryView(CoreProductCategoryView):
    """
    Browse products in a given category
    """
    def get_queryset(self):
        qs = Product.browsable.base_queryset()
        if self.category is not None:
            categories = self.get_categories()
            qs = qs.filter(categories__in=categories).annotate(
                Min("productcategory__priority")).order_by(
                    "productcategory__priority__min", "title").distinct()
        return qs
