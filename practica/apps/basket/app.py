from oscar.apps.basket.app import BasketApplication as CoreApp
from .views import BasketAddAjaxView, BasketView


class BasketApplication(CoreApp):
    add_view = BasketAddAjaxView
    summary_view = BasketView

application = BasketApplication()
