#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from logging import getLogger
log = getLogger("catatlogue.models")


"""
Customized product models
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from oscar.apps.catalogue.abstract_models import (AbstractProduct,
                                                  AbstractProductCategory)
series_name = 'Серии'


# Customizing productcategory model for prioritizing


class ProductCategory(AbstractProductCategory):
    MAIN = 1
    SUBCATEGORY = 2
    DEFAULT = 99
    PRIORITY_CHOICES = (
        (MAIN, u'Основная рубрика'),
        (SUBCATEGORY, u'Дополнительная рубрика'),
        (DEFAULT, u'По умолчанию'),
    )


    priority = models.IntegerField(u'Приоритет', default=99,
                                   choices=PRIORITY_CHOICES,
                                   blank=False,
                                   )


class Product(AbstractProduct):
    authors = models.CharField(u'Авторы',
                               max_length=255, blank=True, null=True)
    contents = models.TextField(u'Оглавление', blank=True, null=True)

    @property
    def serie(self):
        log.debug("in serie")
        Category = self.categories.model
        if Category.objects.filter(name=series_name).exists():
            log.debug("serie category found")
            series_path = Category.objects.get(name=series_name).path
            log.debug("series_path is %s", series_path)
            return self.categories.filter(path__startswith=series_path)[0]


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


from oscar.apps.catalogue.models import *  # noqa
