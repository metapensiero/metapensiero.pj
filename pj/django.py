####jsView
#
# This Django view can be very convenient for dev mode. (Though for production you should obviously use static JS files pre-compiled and minified by your build script.)
#
# **Example:**
#
# **<code>urls.py</code>**:
#<pre>if settings.DEBUG:
#    urlpatterns += patterns('pj.django',
#        url(
#               r'/static/js/mywidget\.js',
#               'jsView',
#               {'main': 'mywidget.main'}),
#    )</pre>
#
# **<code>settings.py</code>**:
#<pre>PJ_PATH = ['...', '...', ...]</pre>

from __future__ import absolute_import

import os, subprocess

from django.http import HttpResponse
from django.template import Context, Template
from django.conf import settings

import pj.api


def jsView(request, **kwargs):
    
    main = kwargs['main']
    path = settings.PJ_PATH
    closureMode = getattr(settings, 'PJ_CLOJURE_MODE', None) or request.GET.get('mode')
    
    js = pj.api.buildBundle(main, path=path)
    
    if kwargs.get('jsPrefix', None):
      js = kwargs['jsPrefix'] + '\n\n' + js
    
    if kwargs.get('renderTemplate', True):
      js = Template(js).render(Context({
        'DEBUG': settings.DEBUG,
      }))
    
    if closureMode:
        js = pj.api.closureCompile(js, closureMode)
    
    return HttpResponse(
                    js.encode('utf-8'),
                    mimetype='text/javascript; charset=utf-8')

