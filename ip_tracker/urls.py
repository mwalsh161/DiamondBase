from django.conf.urls import url

from ip_tracker import views

urlpatterns = [
           url(r'^$', views.index, name='home'),
]

