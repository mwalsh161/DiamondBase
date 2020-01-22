from django.conf.urls import include, url
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth import views as auth_views
import os
from django.contrib import admin
admin.autodiscover()

from DiamondBase import views
from ip_tracker.models import Computer

def my_redirect(name):
    try:
        cpu = Computer.objects.get(name=name)
    except:
        return HttpResponse('Computer does not exist')
    if cpu.notes == 'Error' or cpu.notes == 'Shutting Down':
        return HttpResponse('Machine exists, but either shutdown or error with client.') 
    return HttpResponseRedirect('http://%s'%cpu.ip)

urlpatterns = [
    url(r'^admin/', admin.site.urls,name='admin'),
    url(r'^about/', include(('about.urls', 'about'), namespace='about')),
    url(r'^DB/', include(('sample_database.urls', 'DB'), namespace='DB')),
    url(r'^IP/', include(('ip_tracker.urls', 'IP'), namespace='IP')),
    url(r'^slack/', include(('slack.urls', 'slack'), namespace='slack')),
    url(r'^login/', auth_views.LoginView.as_view(), name='login'),
    url(r'^$',lambda r: HttpResponseRedirect('DB/')),
    url(r'^%s(?P<path>.*)$'%settings.MEDIA_URL[1:],views.media_xsendfile)
]

#if settings.DEBUG:
#    urlpatterns += url(r"%s(?P<path>.*)$" % settings.MEDIA_URL[1:], "static.serve", {"document_root": settings.MEDIA_ROOT,})
