from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from sample_database.models import Action_Type
from django.conf import settings
from ip_tracker.models import *
from ip_tracker.forms import *
from django.db.models import Q

#Helper Classes
class Title:
    def __init__(self,links,current):
        self.links=links
        self.current=current
class Table:
    def __init__(self,head,data):
        self.head=head
        self.data=data

def index(request):
    action_types=Action_Type.objects.filter(~Q(name='Created'))
    order_by = request.GET.get('order','name')
    title = Title([],'%s Computers Registered with diamondbase'%settings.LABNAME)
    #Prepare Data
    computers = Computer.objects.all().order_by(order_by)
    table_head=[(200,'name','Computer Name'),
                (150,'ip','IP Address'),
                (200,'-date_modified','Date Modified'),
                ('',False,'Notes')]
    #Create Table
    table_data=[]
    for comp in computers:
        table_data.append([('/admin/ip_tracker/computer/%i/'%comp.id,comp.name),
                           (False,comp.ip),
                           (False,comp.date_modified),
                           (False,comp.notes)])
    table=Table(table_head,table_data)
    #Prepare html
    context=RequestContext(request,{'action_types':action_types,
                                    'title':title,
                                    'table':table})
    return render(request,'sample_database/base.html',context)

