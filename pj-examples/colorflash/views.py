

from django.shortcuts import render_to_response


def index(request):
    from django.http import HttpResponseRedirect
    return render_to_response('colorflash/index.html')

