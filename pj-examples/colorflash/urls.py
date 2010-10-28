
from django.conf.urls.defaults import *


urlpatterns = patterns('colorflash.views',
    url(r'^$', 'index', name='index'),
)


urlpatterns += patterns('pj.django',
    url(r'^static/js/colorflash\.js$',
            'jsView',
            {'main': 'colorflash.main'},
            name='colorflash_js'),
)