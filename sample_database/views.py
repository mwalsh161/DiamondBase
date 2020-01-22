from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, Http404
from django.utils.safestring import SafeText as SafeString
from django.utils.html import format_html, escape
from django.utils.text import slugify
from django.template import RequestContext, loader
from django.forms.formsets import formset_factory
from django.conf import settings
from sample_database.models import *
from sample_database.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

import re

#SAVE TONS OF CODE BY USING INHERITANCE IN CLASS-BASED views

#Helper Classes
class Title:
    def __init__(self,links,current):
        self.links=links
        self.current=current
class Table:
    def __init__(self,head,data):
        self.head=head
        self.data=data
#Helper Functions
def isPOST(request,formType,instance=False):
    #Returns error or False
    if request.method=='POST':
        if instance:
            form = formType(request.POST,instance=instance)
        else:
            form = formType(request.POST)
        if form.is_valid():
            form.save()
            return False
        else:
            return form.errors
def newlines(string):
    #Start with longest newline char to smallest so we don't duplicate
    string = string.replace('\r\n','<br>')
    string = string.replace('\n\r','<br>')
    string = string.replace('\r','<br>')
    string = string.replace('\n','<br>')
    return SafeString(string)
def find(f,seq):
    #Returns first item in sequence where f(item)==True
    index=0
    for item in seq:
        if f(item):
            return index,item
        index+=1
def format_recent(item):
    if type(item)==Action:
        link = reverse('DB:action_details',args=[item.pieces.all()[0].sample.name,item.pieces.all()[0].name,item.id])
        if item.action_type.name == 'Created':
            target = item.pieces.all()[0]
            samples = ['%s: %s'%(target.sample.name,target.name)]
        else:
            allpieces = item.pieces.all()
            allsamples = list(set([p.sample.name for p in allpieces]))  # Set will make them unique ones only
            samples = allsamples[0:2]
            if len(allsamples) > 2:
                samples.append('...')
        label= "%s (%s)"%(item,', '.join(samples))
        date = item.last_modified.strftime('%B %d, %Y %I:%M %p')
    else:
        link = '/admin/sample_database/design/'+str(item.id)
        label= item.name
        date = item.designattach_set.order_by('-date')[0].date.strftime('%B %d, %Y %I:%M %p')
    if len(item.notes)>50:
        notes = item.notes[0:50]+'...'
    else: notes=item.notes
    if len(notes)>0: date+="  ->  "+notes
    return [[label,link],date]
def format_data_hover(data,label):
    if data.image_file!='':
        content = format_html("<img max-width:512 src={0}><p>{1}</p>",data.get_thumbnail_url(),data.raw_data.name)
    elif data.raw_data=='':
        content = 'No image or data files.'
    else:
        content = data.raw_data.name
    return format_html('<span data-tooltip class="has-tip-right" data-options="disable_for_touch:true" title="{0}">{1}</span>',content,label)

def index(request):
    #Init
    order_by = request.GET.get('order', '-date_created')
    title=Title([],'Welcome to %s Sample Database'%settings.LABNAME)
    #Prepare Data
    samples = Sample.objects.all().order_by(order_by)
    datatables = SafeString('''data-order='[[ 4, "desc" ]]' ''')
    table_head=[(200,False,'Sample Name'),
                (150,False,'Project'),
                (150,False,'Location'),
                ('',False,'Substrate'),
                ('',True,'Date'),
                ('',False,'Notes'),
                ('',False,'')]
    #Create Table
    table_data=[]
    for sample in samples:
        edit_url=reverse('DB:edit',args=['Sample',sample.id])
        delete_url=reverse('DB:delete',args=['Sample',sample.id])
        html=format_html('<a href="{0}?cont={2}">edit</a><br><a href="{1}?cont={2}">delete</a>',edit_url,delete_url,request.get_full_path())
        if sample.name=='None': html=''
        piece_preview = [s.name for s in sample.piece_set.all()[0:3]]
        if sample.piece_set.count() > 3:
            piece_preview.append('...')
        elif len(piece_preview)==0:
            piece_preview = ['No Pieces']
        piece_preview="<br>".join(piece_preview)
        table_data.append([[reverse('DB:sample',args=[sample.name]),format_html('<span data-tooltip data-options="disable_for_touch:true" class="has-tip-bottom" title="{0}">{1}</span>',piece_preview,sample.name)],
                          [False,sample.project],
                          [False,sample.location],
                          [False,sample.substrate],
                          [False,sample.date_created.strftime('%B %d, %Y')],
                          [False,newlines(sample.notes)],
                          [False,html]])
    table=Table(table_head,table_data)
    #Prepare Data - get 5 most recent Actions based on action, general, local dates
    #Also display updates to Designs 
    actions=Action.objects.order_by('-last_modified')
    designs=Design.objects.exclude(design_items=None).order_by('-design_items__design_object_attachment__date')
    #Need to order both of these: Using the fact that they are already ordered to speed things up!
    fields=[]
    while len(fields) < 5 and (len(actions)!=0 or len(designs)!=0):
        if len(designs)==0 and len(actions)!=0:
            fields.append(format_recent(actions[0]))
            actions=actions[1:]
        elif len(actions)==0 and len(designs)!=0:
            fields.append(format_recent(designs[0]))
            designs=designs[1:]
        elif actions[0].last_modified > designs[0].designattach_set.order_by('-date')[0].date:
            fields.append(format_recent(actions[0]))
            actions=actions[1:]
        else:
            fields.append(format_recent(designs[0]))
            designs=designs[1:]
    detail_title='Recent Activity (Pieces and Designs)'
   #Prepare html
    context=RequestContext(request,{'title':title,
                                    'table':table,
                                    'datatables':datatables,
                                    'fields':fields,
                                    'detail_col1':detail_title})
    return render(request,'sample_database/details.html',context)


def newSample(request):
    error = False
    if request.method=='POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user
            sample.save()
            return redirect('DB:sample',sample=sample.name)
        else:
            error = form.errors
    form=SampleForm()
    form.fields["owner"].queryset = User.objects.filter(is_staff=True).order_by('first_name')
    context = RequestContext(request,{'form':form,
                                      'error':error,})
    return render(request,'sample_database/new_sample.html',context)

def sample(request,sample):
    #Init
    order_by = request.GET.get('order', 'name')
    title=Title([(reverse('DB:home'),'Home')],sample)
    sample = Sample.objects.get(name=sample)
    error=False
    if request.method == 'POST':
        form=MapForm(request.POST,request.FILES)
        if form.is_valid():
            map=SampleMap(sample=sample,
                          file=form.cleaned_data['file'],
                          notes=form.cleaned_data['notes'])
            map.save()
        else:
            error = 'Not Valid Entry'
    sample_maps = sample.samplemap_set.order_by('date_created')
    new_piece_url = reverse('DB:new_piece',args=[sample.name])
    #Prepare Data
    pieces = sample.piece_set.order_by('gone',order_by)
    datatables = SafeString('''data-order='[[ 2, "desc" ]]' ''')
    table_head=[(200,False,'Piece Name'),
                (150,False,'Design'),
                ('',True,'Date Created'),
                ('',False,'Gone'),
                ('',False,'')]
    #Create Table
    table_data=[]
    for piece in pieces:
        edit_url=reverse('DB:edit',args=['Piece',piece.id])
        delete_url=reverse('DB:delete',args=['Piece',piece.id])
        html=format_html('<a href="{0}?cont={2}">edit</a><br><a href="{1}?cont={2}">delete</a>',edit_url,delete_url,request.get_full_path())
        ########FORMAT_HTML IS NOT PREVENTING XSS VULERNIBILITY######
        maps = piece.get_maps()
        if len(maps)>0:
            map_url=maps[0].get_thumbnail_url()
            map = format_html('<img src={0}>',map_url)
        else:
            map = 'No map files'
        table_data.append([[reverse('DB:piece',args=[sample.name,piece.name]),format_html('<span data-tooltip class="has-tip-top" data-options="disable_for_touch:true" title="{0}">{1}</span>',map,piece.name)],
                           [False,format_html('<span data-tooltip class="has-tip" title="{0}">{1}</span>',newlines(piece.design.notes), piece.design.name)],
                           [False,piece.date_created.strftime('%B %d, %Y')],
                           [False,str(piece.gone)],
                           [False,html]])
    table=Table(table_head,table_data)
    #Prepare file_upload_form
    form=MapForm()
    #Prepare html
    context = RequestContext(request,{'title':title,
                             'table':table,
                             'new_url':new_piece_url,
                             'upload_form':form,
                             'maps':sample_maps,
                             'error':error,
                             'datatables':datatables,
                             'sample':sample})
    return render(request,'sample_database/sample.html',context)

def newPiece(request,sample):
    error = False
    sample = Sample.objects.get(name=sample)
    if request.method=='POST':
        form = PieceForm(request.POST,instance=Piece(sample=sample))
        if form.is_valid():
            piece = form.save()
            create = piece.action_set.get(action_type__name = 'Created')
            return redirect('DB:action_details',sample.name,piece.name,create.id)
        else:
            error = form.errors
    form=PieceForm()
    context = RequestContext(request,{'error':error,
                                      'sample':sample,
                                      'form':form,
                                      })
    return render(request,'sample_database/new_piece.html',context)

def piece(request,sample,piece):
    #Init
    order_by = request.GET.get('order', 'date')
    s = Sample.objects.get(name=sample)
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample',args=[s.name]),s.name)],piece)
    #Prepare Data
    p = s.piece_set.get(name=piece)
    actions = p.action_set.all().order_by(order_by)
    datatables = SafeString('''data-order='[[ 1, "desc" ]]' ''')
    table_head=[(200,False,'Action'),
                ('150',True,'Date'),
                ('',False,'Notes'),
                ('',False,'')]
    #Create Table
    table_data=[]
    for action in actions:
        label=action.action_type.name
        all_additional_pieces = action.pieces.exclude(name=p.name)
        additional_pieces = [i.name for i in all_additional_pieces[0:1]]
        if len(all_additional_pieces) > 1:
            additional_pieces.append('...')
        if len(additional_pieces) > 0:
            label += ' (%s)'%(', '.join(additional_pieces))
        edit_url=reverse('DB:edit',args=['Action',action.id])
        delete_url=reverse('DB:delete',args=['Action',action.id])
        html=format_html('<a href="{0}?cont={2}">edit</a><br><a href="{1}?cont={2}">delete</a>',edit_url,delete_url,request.get_full_path())
        if action.action_type.name=='Created': html=''
        table_data.append([[reverse('DB:action_details',args=[s.name,p.name,action.id]),label],
                          [False,action.date.strftime('%B %d, %Y %I:%M %p')],
                          [False,newlines(action.notes)],
                          [False,html]])
    table=Table(table_head,table_data)
    #Prepare html
    context = RequestContext(request,{'title':title,
                             'table':table,
                             'piece':p,
                             'datatables':datatables,
                             'sample':s})
    return render(request,'sample_database/piece.html',context)

def actionDetails(request,sample,piece,actionID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(name=sample)
    p = s.piece_set.get(name=piece)
    a = Action.objects.get(id=actionID)
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample',args=[s.name]),s.name),
                 (reverse('DB:piece',args=[s.name,p.name]),p.name)],
                a.action_type.name+' ('+a.date.strftime('%B %d, %Y %I:%M %p')+')')
    error=None
    #Prepare Data
    field_names=[el for el in a.action_type.field_names.splitlines() if len(el)>0]
    field_names.append('Notes')
    field_data=[el for el in a.fields.splitlines() if len(el)>0]
    field_data.append(newlines(a.notes))
    fields=zip(field_names,field_data)
    data= a.general_set.order_by(order_by)
    #On POST
    if request.method=='POST':
        #Need to validate form to get data_type; then validate for real
        form=GeneralDataForm([],request.POST)
        form.is_valid()
        data_type=form.cleaned_data['data_type']
        POST_fields=[el for el in data_type.field_names.splitlines() if len(el)>0]
        #Generate form for data_type as determined above then actually validate
        form=GeneralDataForm(POST_fields,request.POST,request.FILES)
        if form.is_valid():
            data_type=form.cleaned_data['data_type']
            POST_fields=[el for el in data_type.field_names.splitlines() if len(el)>0]
            f=''
            for POST_field in POST_fields:
                f+=form.cleaned_data[POST_field]+'\r\n'
            new_data=General(data_type=data_type,
                             fields=f,
                             image_file=form.cleaned_data['image_file'],
                             raw_data=form.cleaned_data['raw_data'],
                             notes=form.cleaned_data['notes'],
                             xmin=form.cleaned_data['xmin'],
                             xmax=form.cleaned_data['xmax'],
                             ymin=form.cleaned_data['ymin'],
                             ymax=form.cleaned_data['ymax'],
                             parent=a)
            new_data.save()
        else:
            error = form.errors
    #Prepare Table
    datatables = SafeString('''data-order='[[ 1, "desc" ]]' ''')
    table_head=[(200,False,'Type'),
                ('',True,'Date'),
                ('',False,'Notes'),
                ('',False,'')]
    table_data=[]
    for dat in data:
        edit_url=reverse('DB:edit',args=['General',dat.id])
        delete_url=reverse('DB:delete',args=['General',dat.id])
        html=format_html('<a href="{0}?cont={2}">edit</a><br><a href="{1}?cont={2}">delete</a>',edit_url,delete_url,request.get_full_path())
        table_data.append([[reverse('DB:general_details',args=[s.name,p.name,dat.id]),format_data_hover(dat,dat.data_type.name)],
                           [False,dat.date.strftime('%B %d, %I:%M %p')],
                           [False,newlines(dat.notes)],
                           [False,html]])
    table=Table(table_head,table_data)
    #Prepare Form
    form=[]
    for type in data_types:
        f = [el for el in type.field_names.splitlines() if len(el)>0]
        f_temp=GeneralDataForm(f,initial={'data_type':type})
        form.append([type.name,f_temp])
    #Prepare html
    context = RequestContext(request,{'title':title,
                             'table':table,
                             'action':a,
                             'datatables':datatables,
                             'other_pieces':a.pieces.exclude(id=p.id),
                             'fields':fields,
                             'modal_form':form,
                             'data_types':data_types,
                             'error':error,
                             'obj':a,
                             'add_zip':True})
    return render(request,'sample_database/Modal_form.html',context)

def generalDetails(request,sample,piece,generalID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(name=sample)
    p = s.piece_set.get(name=piece)
    g = General.objects.get(id=generalID)
    a = g.parent
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample',args=[s.name]),s.name),
                 (reverse('DB:piece',args=[s.name,p.name]),p.name),
                 (reverse('DB:action_details',args=[s.name,p.name,a.id]),a.action_type.name+' ('+a.date.strftime('%B %d, %Y')+')')],
                g.data_type.name+' ('+g.date.strftime('%I:%M %p')+')')
    error=None
    #Prepare Data
    field_names=[el for el in g.data_type.field_names.splitlines() if len(el)>0]
    field_names+=['xmin','xmax','ymin','ymax','Notes']
    field_data=[el for el in g.fields.splitlines() if len(el)>0]
    field_data+=[g.xmin,g.xmax,g.ymin,g.ymax,newlines(g.notes)]
    fields=zip(field_names,field_data)
    data= g.local_set.order_by(order_by)
    #On POST
    if request.method=='POST':
        form=LocalDataForm([],request.POST,request.FILES)
        form.is_valid()
        data_type=form.cleaned_data['data_type']
        POST_fields=[el for el in data_type.field_names.splitlines() if len(el)>0]
        form=LocalDataForm(POST_fields,request.POST,request.FILES)
        if form.is_valid():
            data_type=form.cleaned_data['data_type']
            POST_fields=[el for el in data_type.field_names.splitlines() if len(el)>0]
            f=''
            for POST_field in POST_fields:
                f+=form.cleaned_data[POST_field]+'\r\n'
            new_data=Local(data_type=data_type,
                             fields=f,
                             image_file=form.cleaned_data['image_file'],
                             raw_data=form.cleaned_data['raw_data'],
                             notes=form.cleaned_data['notes'],
                             x=form.cleaned_data['x'],
                             y=form.cleaned_data['y'],
                             parent=g)
            new_data.save()
        else:
            error=form.errors
    #Prepare Table
    datatables = SafeString('''data-order='[[ 1, "desc" ]]' ''')
    table_head=[(200,False,'Type'),
                ('',True,'Time'),
                ('',False,'Notes'),
                ('',False,'')]
    table_data=[]
    for dat in data:
        edit_url=reverse('DB:edit',args=['Local',dat.id])
        delete_url=reverse('DB:delete',args=['Local',dat.id])
        html=format_html('<a href="{0}?cont={2}">edit</a><br><a href="{1}?cont={2}">delete</a>',edit_url,delete_url,request.get_full_path())
        table_data.append([[reverse('DB:local_details',args=[s.name,p.name,dat.id]),format_data_hover(dat,dat.data_type.name)],
                           [False,dat.date.strftime('%I:%M %p')],
                           [False,newlines(dat.notes)],
                           [False,html]])
    table=Table(table_head,table_data)
    #Prepare Form
    form=[]
    for type in data_types:
        f = [el for el in type.field_names.splitlines() if len(el)>0]
        f_temp=LocalDataForm(f,initial={'data_type':type})
        form.append([type.name,f_temp])
    #Prepare html
    context = RequestContext(request,{'title':title,
                             'table':table,
                             'fields':fields,
                             'modal_form':form,
                             'datatables':datatables,
                             'data_types':data_types,
                             'error':error,
                             'raw':g.raw_data,
                             'file':g.image_file,
                             'obj':g})
    return render(request,'sample_database/Modal_form.html',context)

def localDetails(request,sample,piece,localID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(name=sample)
    p = s.piece_set.get(name=piece)
    l = Local.objects.get(id=localID)
    g = l.parent
    a = g.parent
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample',args=[s.name]),s.name),
                 (reverse('DB:piece',args=[s.name,p.name]),p.name),
                 (reverse('DB:action_details',args=[s.name,p.name,a.id]),a.action_type.name+' ('+a.date.strftime('%B %d, %Y')+')'),
                 (reverse('DB:general_details',args=[s.name,p.name,g.id]),g.data_type.name+' ('+g.date.strftime('%I:%M %p')+')')],
                l.data_type.name)
    error=None
    #Prepare Data
    field_names=[el for el in l.data_type.field_names.splitlines() if len(el)>0]
    field_names+=['x','y','Notes']
    field_data=[el for el in l.fields.splitlines() if len(el)>0]
    field_data+=[l.x,l.y,newlines(l.notes)]
    fields=zip(field_names,field_data)
    data= l.local_attachment_set.order_by(order_by)
    #On POST
    if request.method=='POST':
        form=AttachmentForm([],request.POST,request.FILES)
        form.is_valid()
        data_type=form.cleaned_data['data_type']
        POST_fields=[el for el in data_type.field_names.splitlines() if len(el)>0]
        form=AttachmentForm(POST_fields,request.POST,request.FILES)
        if form.is_valid():
            data_type=form.cleaned_data['data_type']
            POST_fields=[el for el in data_type.field_names.splitlines() if len(el)>0]
            f=''
            for POST_field in POST_fields:
                f+=form.cleaned_data[POST_field]+'\r\n'
            new_data=Local_Attachment(data_type=data_type,
                           fields=f,
                           image_file=form.cleaned_data['image_file'],
                           raw_data=form.cleaned_data['raw_data'],
                           notes=form.cleaned_data['notes'],
                           parent=l)
            new_data.save()
        else:
            error=form.errors
    #Prepare Table
    datatables = SafeString('''data-order='[[ 1, "desc" ]]' ''')
    table_head=[(200,False,'Type'),
                ('',True,'Date'),
                ('',False,'Notes'),
                ('',False,'')]
    table_data=[]
    for dat in data:
        edit_url=reverse('DB:edit',args=['Local_Attachment',dat.id])
        delete_url=reverse('DB:delete',args=['Local_Attachment',dat.id])
        html=format_html('<a href="{0}?cont={2}">edit</a><br><a href="{1}?cont={2}">delete</a>',edit_url,delete_url,request.get_full_path())
        table_data.append([[reverse('DB:attach_details',args=[s.name,p.name,dat.id]),format_data_hover(dat,dat.data_type.name)],
                           [False,dat.date.strftime('%B %d, %Y')],
                           [False,newlines(dat.notes)],
                           [False,html]])
    table=Table(table_head,table_data)
    #Prepare Form
    form=[]
    for type in data_types:
        f = [el for el in type.field_names.splitlines() if len(el)>0]
        f_temp=AttachmentForm(f,initial={'data_type':type})
        form.append([type.name,f_temp])
    #Prepare html
    context = RequestContext(request,{'title':title,
                             'table':table,
                             'fields':fields,
                             'datatables':datatables,
                             'modal_form':form,
                             'data_types':data_types,
                             'error':error,
                             'raw':l.raw_data,
                             'file':l.image_file,
                             'obj':l})
    return render(request,'sample_database/Modal_form.html',context)

def attachDetails(request,sample,piece,attachID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(name=sample)
    p = s.piece_set.get(name=piece)
    att=Local_Attachment.objects.get(id=attachID)
    l = att.parent
    g = l.parent
    a = g.parent
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample',args=[s.name]),s.name),
                 (reverse('DB:piece',args=[s.name,p.name]),p.name),
                 (reverse('DB:action_details',args=[s.name,p.name,a.id]),a.action_type.name+' ('+a.date.strftime('%B %d, %Y')+')'),
                 (reverse('DB:general_details',args=[s.name,p.name,g.id]),g.data_type.name+' ('+g.date.strftime('%B %d, %Y')+')'),
                 (reverse('DB:local_details',args=[s.name,p.name,l.id]),l.data_type.name+' ('+l.date.strftime('%B %d, %Y')+')')],
                att.data_type.name+' ('+att.date.strftime('%B %d, %Y')+')')
    #Prepare Data
    field_names=[el for el in att.data_type.field_names.splitlines() if len(el)>0]
    field_names+=['Notes']
    field_data=[el for el in att.fields.splitlines()]
    field_data+=[newlines(att.notes)]
    fields=zip(field_names,field_data)
    #Prepare html
    context = RequestContext(request,{'title':title,
                             'fields':fields,
                             'raw':att.raw_data,
                             'file':att.image_file,
                             'obj':att})
    return render(request,'sample_database/Modal_form.html',context)

def newAction(request,action_type):
    error=False
    a_type = Action_Type.objects.get(name=action_type)
    fields = [el for el in a_type.field_names.splitlines() if len(el)>0]
    if request.method=='POST':
        form=ActionForm(fields,request.POST)
        if form.is_valid():
            f=''
            pieces=[]
            for field in fields:
                f+=form.cleaned_data[field]+'\r\n'
            for sample in Sample.objects.all():
                if len(sample.piece_set.all())>0:
                    pieces+=form.cleaned_data[sample.name]
            new_action=Action(action_type=a_type,
                              fields=f,
                              owner=request.user,
                              last_modified_by = request.user,
                              notes=form.cleaned_data['notes'],
                              date =form.cleaned_data['date'])
            new_action.save()
            for p in pieces:
                new_action.pieces.add(p)
            if len(new_action.pieces.all())<1:
                new_action.delete()
                error = 'An action requires 1 or more pieces!'
                context = RequestContext(request,{'error':error,'form':form,'a_type':a_type})
                return render(request,'sample_database/new_action.html',context)
            return redirect('DB:home')
        else:
            error = form.errors
    else:
        form=ActionForm(fields)
    # Split form up to properties and samples
    form_props = []
    form_samples = []
    for field in form:
        temp = {'errors':field.errors,
                'help_text':field.help_text,
                'label_tag':field.label_tag(),
                'field':field.__unicode__()}
        if field.help_text == 'sample':
            form_samples.append(temp)
        else:
            form_props.append(temp)
    context = RequestContext(request,{'error':error,'form_props':form_props,'form_samples':form_samples,'a_type':a_type})
    return render(request,'sample_database/new_action.html',context)

def edit(request,type,id):
    prompt="Changes are permanent (under construction)"
#    action_types=Action_Type.objects.filter(~Q(name='Created'))
    editable=['Piece','Sample','Action','General','Local','Local_Attachment']
    error=False
    obj=False
    form=''
    fields=''
    if type not in editable:
        error= "%s not editable or does not exist"%type
    else:
        obj=eval(type+".objects.get(id=%s)"%id)
        obj.last_modified_by = request.user
        error=isPOST(request,eval("edit_%s"%type),obj)
        form=eval("edit_%s(instance=obj)"%type)
        if type == 'Action':
            fields=[el for el in obj.action_type.field_names.splitlines() if len(el)>0]
        elif type == 'Sample':
            form.fields["owner"].queryset = User.objects.filter(is_staff=True).order_by('first_name')
        elif type != 'Sample' and type != 'Piece':
            fields=[el for el in obj.data_type.field_names.splitlines() if len(el)>0]
        if not error and request.POST:
            continue_url = request.GET.get('cont')
            if continue_url:
                return redirect(continue_url)
            try: return redirect(obj.url())
            except: pass  # If not url method, just return this form
    context = RequestContext(request,{'obj':obj,
                                      'obj_fields':fields,
                                      'error':error,
                                      'type':type,
                                      'caller':'Edit',
                                      'prompt':prompt,
                                      'edit_form':form})
    return render(request,'sample_database/edit.html',context)

def delete(request,type,id):
    error=False
    obj=False
    form=''
    prompt=''
    editable=['Sample','Piece','Action','General','Local','Local_Attachment']
    caller='Delete'
    if type not in editable:
        error = "%s not editable or does not exist"%type
    if type=='Action' or type=='Sample':
        if type=='Action':name= eval(type+".objects.get(id=%s)"%id).action_type.name
        if type=='Sample':name= eval(type+".objects.get(id=%s)"%id).name
        if name=='None' or name=='Created':
            error="%s %s is not deletable"%(type,name)
    if not error:
        obj=eval(type+".objects.get(id=%s)"%id)
        if request.POST:
            obj.delete()
            continue_url = request.GET.get('cont')
            if continue_url:
                return redirect(continue_url)
            else:
                return redirect(reverse('DB:home'))
        else:
            children_type=[el for el in dir(obj) if len(re.findall("_set$",el))]
            direct=0
            for child_type in children_type:
                child=getattr(obj,child_type).all()
                direct+=len(child)
            prompt="Are you sure you want to delete this and %i direct children?<br><br><b>The action is permanent!</b>"%direct
    context = RequestContext(request,{'obj':obj,
                                      'error':error,
                                      'type':type,
                                      'caller':caller,
                                      'prompt':SafeString(prompt)})
    return render(request,'sample_database/edit.html',context)

def upload_zip(request,type,parent_id):
    error=False
    parent = Action.objects.get(id=parent_id)
    type = Data_Type.objects.get(name=type)
    prompt='Filenames will go to notes unless a txt file is supplied.  The txt file needs<b> one line per file!!</b>'
    if request.method == 'POST':
        form=ZipForm(type,request.POST,request.FILES)
        if form.is_valid():
            NEXT = form.cleaned_data['referrer']
            out, error = form.save(parent,type)
            if not error:
                return redirect(NEXT)
            else:
                error = out
        else:
            error = form.errors
    NEXT = request.GET.get('next','DB:home')
    form=ZipForm(type,initial={'referrer':NEXT})
    context = RequestContext(request,{'parent':parent,
                                      'type':type,
                                      'error':error,
                                      'form':form,
                                      'prompt':SafeString(prompt)})
    return render(request,'sample_database/upload_zip.html',context)

