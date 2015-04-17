#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from logging import getLogger
log = getLogger("practica.middleware")

from django.contrib import messages
import json


class AjaxMessaging(object):
    def process_response(self, request, response):
        for message in messages.get_messages(request):
            log.debug(message)
        if request.is_ajax():
            if response['Content-Type'] in ["application/javascript",
                                            "application/json"]:
                try:
                    content = json.loads(response.content)
                except ValueError:
                    return response

                django_messages = []

                for message in messages.get_messages(request):

                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })

                content['django_messages'] = django_messages

                response.content = json.dumps(content)
        return response


from cProfile import Profile
from pstats import Stats
import StringIO

from django.conf import settings
if hasattr(settings, "PSTATS_SORT_TUPLE"):
    sort_tuple = settings.PSTATS_SORT_TUPLE
else:
    sort_tuple = ('time', 'calls')


class ProfileMiddleware(object):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.

    WARNING: It uses cProfile

    """

    def process_request(self, request):
        if self.is_on(request):
            self.prof = Profile()

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.is_on(request):
            log.debug("%s called", callback)
            callback_args = (request,) + callback_args
            return self.prof.runcall(
                callback, *callback_args, **callback_kwargs)

    def process_response(self, request, response):
        if self.is_on(request):
            self.prof.create_stats()
            out = StringIO.StringIO()
            stats = Stats(self.prof, stream=out)

            stats.sort_stats(*sort_tuple)

            stats.print_stats()

            stats_str = out.getvalue()

            if response and response.content and stats_str:
                response.content = "<pre>" + stats_str + "</pre>"
        return response

    def is_on(self, request):
        return (settings.DEBUG or request.user.is_superuser)\
            and 'prof' in request.GET
