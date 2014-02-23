from django.http import HttpResponse
def raise_error(request):
    raise ValueError ("Here comes error test")
    return HttpResponse("This is not supposed to be seen")
