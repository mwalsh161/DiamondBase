from django.conf.urls import patterns, url

from ip_tracker import views

urlpatterns = patterns('',
           url(r'^$', views.index, name='home'),
            )

