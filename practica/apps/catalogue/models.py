# set encoding=utf-8

"""
Customized product models
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from oscar.apps.catalogue.abstract_models import AbstractProduct

class Product(AbstractProduct):
    authors = models.CharField(u'Авторы', max_length=255, blank=True, null=True)
    contents = models.TextField(u'Оглавление', blank=True, null=True)

class ProductFragment(models.Model):
    """
    Фрагменты
    """
    product = models.ForeignKey(
        'catalogue.Product', related_name='fragments', verbose_name=_("Product"))
    original = models.FileField(
        u"Фрагмент", upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255)
    caption = models.CharField(
        _("Caption"), max_length=200, blank=True, null=True)

    #: Use display_order to determine which is the "primary" image
    display_order = models.PositiveIntegerField(
        _("Display Order"), default=0,
        help_text=u"Порядок расположения примеров на странице")
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    class Meta:
        unique_together = ("product", "display_order")
        ordering = ["display_order"]
        verbose_name = u'Фрагмент'
        verbose_name_plural = u'Фрагменты'

    def __unicode__(self):
        return u"%s (фрагмент из '%s')" % (self.caption, self.product)


from oscar.apps.catalogue.models import *
