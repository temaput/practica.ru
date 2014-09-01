from django.db import models
from django.utils.translation import ugettext as _

from oscar.apps.payment import abstract_models


class SourceType(abstract_models.AbstractSourceType):
    description = models.TextField(
        _("Description"),
        help_text=_("Can contain raw html"), blank=True)
    is_defered = models.BooleanField(
        _("Defered payment"),
        help_text=_("User may pay later"), default=False)

from oscar.apps.payment.models import *
