from django.conf import settings

def metadata(request):
    return dict(
            yandex_metrika_id=getattr(settings, 'YANDEX_METRIKA_ID', None),
            )
