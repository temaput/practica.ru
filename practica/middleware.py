#!/usr/bin/env python
#vi:fileencoding=utf-8
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
            if response['Content-Type'] in ["application/javascript", "application/json"]:
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
