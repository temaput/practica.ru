#!/usr/bin/env python
#vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from .views import PracticaHomeView
from oscar.apps.promotions.app import PromotionsApplication as CoreApp

class PromotionsApplication(CoreApp):
    home_view = PracticaHomeView

application = PromotionsApplication()
