#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import OldSiteSwapper

urlpatterns = patterns(
    '',
    # /Books/[xxx.html]
    url(r"^(?P<old_href>.*\.html)$", OldSiteSwapper.as_view(),
        name="oldsite_swapper_view"),
)
