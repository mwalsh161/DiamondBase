from django.conf.urls import patterns, include, url
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.views import login
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

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls),name='admin'),
    url(r'^about/', include('about.urls', namespace='about')),
    url(r'^DB/', include('sample_database.urls',namespace='DB')),
    url(r'^IP/', include('ip_tracker.urls',namespace='IP')),
    url(r'^slack/', include('slack.urls',namespace='slack')),
    url(r'^login/', login, name='login'),
    url(r'^$',lambda r: HttpResponseRedirect('DB/')),
    url(r'^%s(?P<path>.*)$'%settings.MEDIA_URL[1:],views.media_xsendfile)
)

if settings.DEBUG:
    urlpatterns += patterns("django.views",
                            url(r"%s(?P<path>.*)$" % settings.MEDIA_URL[1:], "static.serve", {"document_root": settings.MEDIA_ROOT,})
                            )
