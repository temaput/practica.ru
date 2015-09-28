#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView
from .views import OldSiteSwapper

urlpatterns = patterns(
    '',
    # /Books/[xxx.html]
    url(r"^cart.htm$", RedirectView.as_view(url='/OldCatalog/cart.htm')),
    url(r"^index.html$", RedirectView.as_view(url='/')),
    url(r"^(?P<old_href>.*\.html)$", OldSiteSwapper.as_view(),
        name="oldsite_swapper_view"),
    url(r"", RedirectView.as_view(url='/')),
)
