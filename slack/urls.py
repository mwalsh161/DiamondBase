from django.conf.urls import url
from slack import views

urlpatterns = [
           url(r'^acidclean/$',views.slash_acidclean, name='acidclean'),
]
