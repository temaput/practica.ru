from oscar.apps.dashboard.app import DashboardApplication as CoreDashboard
from catalogue.app import application as catalogue_app

class DashboardApplication(CoreDashboard):
    catalogue_app = catalogue_app

application = DashboardApplication()
