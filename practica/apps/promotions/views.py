from django.views.generic.list import ListView
from django.conf import settings
from django.db.models import get_model, Min
from django.core.exceptions import ObjectDoesNotExist

Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')

# Create your views here.


class PracticaHomeView(ListView):
    """
    Display goods from gategory Na glavnoi
    """
    context_object_name = "products"
    template_name = 'promotions/home.html'

    def get_queryset(self):
        qs = Product.browsable.base_queryset()
        self.base_qs = qs.all()
        try:
            cat = Category.objects.get(slug=settings.HOME_PAGE_CATEGORY_SLUG)
            self.qs = qs.filter(categories=cat).annotate(
                Min("productcategory__priority")).order_by(
                    "productcategory__priority__min", "title").distinct()
            return self.qs
        except ObjectDoesNotExist:
            return qs.all()

    def get_context_data(self, **kwargs):
        context = super(PracticaHomeView, self).get_context_data(**kwargs)
        context['highlights'] = self.get_highlights()
        return context

    def get_highlights(self):
        try:
            banners_category = Category.objects.get(
                name=settings.HOME_BANNERS_CATEGORY_NAME)
            return self.base_qs.filter(categories=banners_category)
        except ObjectDoesNotExist:
            return self.base_qs.none()

