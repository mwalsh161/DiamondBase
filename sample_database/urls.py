from django.conf.urls import url

from sample_database import views

urlpatterns = [
           url(r'^$', views.index, name='home'),
           url(r'^upload_zip/attachment(?P<attachID>([^\/]+))/(?P<parent_id>[0-9]+)/$',views.upload_zip,name='upload_zip'),
           url(r'^new_sample/$',views.newSample, name='new_sample'),
           url(r'^edit/(?P<type>([^\/]+))/ID(?P<id>([^\/]+))/$',views.edit,name='edit'),
           url(r'^delete/(?P<type>([^\/]+))/ID(?P<id>([^\/]+))/$',views.delete,name='delete'),
           url(r'^(?P<sampleID>([^\/]+))/new_piece/$', views.newPiece, name='new_piece'),
           url(r'^new_(?P<action_type>([^\/]+))/$', views.newAction, name='new_action'),
           url(r'^design_item/$', views.design_item, name='design_item'),
           url(r'^design_item/(?P<design_itemID>([^\/]+))/$', views.design_item_detail, name='design_item_detail'),
           url(r'^design/$', views.design, name='design'),
           url(r'^(?P<sampleID>([^\/]+))/$', views.sample ,name='sample'),
           url(r'^(?P<sampleID>([^\/]+))/(?P<pieceID>([^\/]+))/$', views.piece ,name='piece'),
           url(r'^(?P<sampleID>([^\/]+))/(?P<pieceID>([^\/]+))/action(?P<actionID>([^\/]+))/$', views.actionDetails ,name='action_details'),
           url(r'^(?P<sampleID>([^\/]+))/(?P<pieceID>([^\/]+))/general_dat(?P<generalID>([^\/]+))/$', views.generalDetails ,name='general_details'),
           url(r'^(?P<sampleID>([^\/]+))/(?P<pieceID>([^\/]+))/local_dat(?P<localID>([^\/]+))/$', views.localDetails ,name='local_details'),
           url(r'^(?P<sampleID>([^\/]+))/(?P<pieceID>([^\/]+))/attachment(?P<attachID>([^\/]+))/$', views.attachDetails ,name='attach_details')
]

##Modify to use something like "slugs" by adding a slugify function to views, and only look for a match at the beginning of url
