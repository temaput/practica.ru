from django.shortcuts import render
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
                slug=settings.HOME_PAGE_CATEGORY_SLUG).product_set.all()
