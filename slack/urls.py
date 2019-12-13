from django.conf.urls import patterns, url
from slack import views

urlpatterns = patterns('',
           url(r'^acidclean/$',views.slash_acidclean, name='acidclean'),
        )
