
from django.http import HttpResponse
from django.template  import Context, loader


def writePost(request):
    print request
    # parse request
    return(HttpResponse("writePost"))