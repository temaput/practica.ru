from oscar.apps.dashboard.catalogue.app import CatalogueApplication as \
        CoreCatalogueApp
from views import ProductCreateUpdateView

class CatalogueApplication(CoreCatalogueApp):
    product_createupdate_view = ProductCreateUpdateView

application = CatalogueApplication()
