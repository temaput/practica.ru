from django.views.generic.list import ListView
from django.conf import settings
from django.db.models import get_model

Category = get_model('catalogue', 'Category')

# Create your views here.


class PracticaHomeView(ListView):
    """
    Display goods from gategory Na glavnoi
    """
    context_object_name = "products"
    template_name = 'promotions/home.html'

    def get_queryset(self):
        return Category.objects.get(
            slug=settings.HOME_PAGE_CATEGORY_SLUG).product_set.order_by(
            "title")

    def get_context_data(self, **kwargs):
        context = super(PracticaHomeView, self).get_context_data(**kwargs)
        context['highlights'] = self.get_highlights()
        return context

    def get_highlights(self):
        banners_category = Category.objects.get(
            name=settings.HOME_BANNERS_CATEGORY_NAME)
        return banners_category.product_set.all()
