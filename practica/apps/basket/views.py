from logging import getLogger
log = getLogger("basket.views")

import json
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render
from django.core.urlresolvers import reverse

from oscar.apps.basket.views import BasketAddView, BasketView

# Create your views here.

class JSONResponseMixin(object):
    def render_to_response(self, context):
        log.debug("in JSON render_to_response")
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        return HttpResponse(content, content_type='application/json', **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)

class BasketAddAjaxView(JSONResponseMixin, BasketAddView):

    def form_valid(self, form):
        response = super(BasketAddAjaxView, self).form_valid(form)
        if self.request.is_ajax():
            mini_basket_html = render_to_string(
                    'partials/mini_basket.html',
                    RequestContext(self.request, {})
                    )
            body = {'mini_basket': mini_basket_html}
                        
            return JSONResponseMixin.render_to_response(self, 
                    { 'status': 'OK', 'body': body })
        else:
            return response

    def form_invalid(self, form):
        response = super(BasketAddAjaxView, self).form_invalid(form)
        if self.request.is_ajax():
            log.debug("basket_form.errors: %s", form.errors)
            basket_form_html = render_to_string(
                    'catalogue/partials/add_to_basket_form_core.html', 
                    RequestContext(self.request, { 
                        'basket_form': form,
                        'product': form.instance,
                        })
                    )
            context = {'status': 'error', 'body': basket_form_html}
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return response

class BasketView(BasketView):
    def get_success_url(self):
        if 'next' in self.request.REQUEST:
            return self.request.REQUEST.get('next')
        return self.request.META.get('HTTP_REFERER', reverse('basket:summary'))
