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
            form = formType(request.POST, request.FILES, instance=instance)
        else:
            form = formType(request.POST, request.FILES)
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
        link = reverse('DB:action_details',args=[item.pieces.all()[0].sample.id, item.pieces.all()[0].id, item.id])
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
        link = reverse('DB:design') + '?edit=' + str(item.id)
        label= item.name
        attachments = Design_Object_Attachment.objects.filter(design_object__design__id=item.id).order_by('-date')
        date = ''
        if len(attachments) > 0:
            date = attachments[0].date.strftime('%B %d, %Y %I:%M %p')
    if len(item.notes)>50:
        notes = item.notes[0:50]+'...'
    else: notes=item.notes
    if len(notes)>0: date+="  ->  "+notes
    return [[label,link],date]
def format_data_hover(data,label):
    if hasattr(data, 'image_file') and data.image_file != '':
        if hasattr(data, 'raw_data'):
            content = format_html("<img max-width:512 src={0}><p>{1}</p>", data.get_thumbnail_url(), data.raw_data.name)
        else:
            content = format_html("<img max-width:512 src={0}>", data.get_thumbnail_url())
    elif hasattr(data, 'file') and data.file.name:
        content = format_html("<img max-width:512 src={0}>", data.file.url)
    elif not hasattr(data, 'raw_data') or data.raw_data=='':
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
        table_data.append([[reverse('DB:sample', args=[sample.id]), format_html('<span data-tooltip data-options="disable_for_touch:true" class="has-tip-bottom" title="{0}">{1}</span>', piece_preview, sample.name)],
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
        if len(designs) > 0:
            attachments = Design_Object_Attachment.objects.filter(design_object__design__id=designs[0].id).order_by('-date')

        if len(designs)==0 and len(actions)!=0:
            fields.append(format_recent(actions[0]))
            actions=actions[1:]
        elif len(actions)==0 and len(designs)!=0:
            fields.append(format_recent(designs[0]))
            designs=designs[1:]
        elif len(attachments) > 0 and actions[0].last_modified > attachments[0].date:
            fields.append(format_recent(actions[0]))
            actions=actions[1:]
        else:
            if len(attachments) > 0:
                fields.append(format_recent(designs[0]))
            designs=designs[1:]
    detail_title='Recent Activity (Pieces and Designs)'
   #Prepare html
    context=RequestContext(request,{'title':title,
                                    'table':table,
                                    'datatables':datatables,
                                    'fields':fields,
                                    'detail_col1':detail_title}).flatten()
    return render(request,'sample_database/details.html',context)

def design(request):
    if request.method == 'POST':
        if request.POST.__contains__('new'):
            new_item = Design(name='New Design', notes='', vector_file='', image_file='')
            new_item.save()

            return redirect(reverse('DB:edit', args=['Design', new_item.id]) + '?cont=' + reverse('DB:design'))

    #Init
    order_by = request.GET.get('order', 'name')
    items = Design.objects.all().order_by(order_by)
    
    #Prepare Data
    datatables = SafeString('''data-order='[[ 0, "desc" ]]' ''')
    table_head = [(200,True,'Name'),
                 ('',False,'Notes'),
                 ('',False,'')]

    #Create Table
    table_data = []
    for item in items:
        label = item.name
        this_url = reverse('DB:design')
        edit_url = reverse('DB:edit', args=['Design', item.id])
        del_url = reverse('DB:delete', args=['Design', item.id])
        html = format_html('<a href="{1}?cont={0}">edit</a><br><a href="{2}?cont={0}">delete</a>', this_url, edit_url, del_url)
        table_data.append([[False, format_data_hover(item, label)],
                          [False, newlines(item.notes)],
                          [False, html]])
    table = Table(table_head, table_data)

    #Prepare html
    context = RequestContext(request,{'table':table,
                             'datatables':datatables}).flatten()

    return render(request, 'sample_database/edit_design.html', context)

def design_item(request):
    if request.method == 'POST':
        if request.POST.__contains__('new'):
            new_item = Design_Item(name='New Design Item', notes='')
            new_item.save()

            return redirect(reverse('DB:edit', args=['Design_Item', new_item.id]) + '?cont=' + reverse('DB:design_item'))

    #Init
    order_by = request.GET.get('order', 'name')
    items = Design_Item.objects.all().order_by(order_by)
    
    #Prepare Data
    datatables = SafeString('''data-order='[[ 0, "desc" ]]' ''')
    table_head = [(200,True,'Name'),
                 ('',False,'Notes'),
                 ('',False,'')]

    #Create Table
    table_data = []
    for item in items:
        label = format_html('<a href="{0}">{1}</a>', reverse('DB:design_item_detail', args=[item.id]), item.name)
        this_url = reverse('DB:design_item')
        edit_url = reverse('DB:edit', args=['Design_Item', item.id])
        del_url = reverse('DB:delete', args=['Design_Item', item.id])
        html = format_html('<a href="{1}?cont={0}">edit</a><br><a href="{2}?cont={0}">delete</a>', this_url, edit_url, del_url)
        num_attachments = Design_Object_Attachment.objects.filter(design_object = item).count()
        if num_attachments > 0:
            num_attachments_text = '{0} attachment'.format(num_attachments) if num_attachments == 1 else '{0} attachments'.format(num_attachments)
        else:
            num_attachments_text = 'No attachments'
        label_html = format_html('<span data-tooltip class="has-tip-right" data-options="disable_for_touch:true" title="{0}">{1}</span>',num_attachments_text, label)
        table_data.append([[False, label_html],
                          [False, newlines(item.notes)],
                          [False, html]])
    table = Table(table_head, table_data)

    #Prepare html
    context = RequestContext(request,{'table':table,
                             'datatables':datatables}).flatten()
    return render(request, 'sample_database/edit_design_item.html', context)

def design_item_detail(request, design_itemID):
    Item = Design_Item.objects.get(id = design_itemID)
    
    if request.method == 'POST':
        if request.POST.__contains__('new'):
            new_item = Design_Object_Attachment(design_object=Item, name='New Design Item Attachment', notes='')
            new_item.save()

            return redirect(reverse('DB:edit', args=['Design_Object_Attachment', new_item.id]) + '?cont=' + reverse('DB:design_item_detail', args=[Item.id]))


    order_by = request.GET.get('order', 'date')
    Attachments = Design_Object_Attachment.objects.filter(design_object = Item).order_by(order_by)

    #Prepare Data
    datatables = SafeString('''data-order='[[ 1, "desc" ]]' ''')
    table_head = [(200,True,'Name'),
                 ('',False,'Date'),
                 ('',False,'Notes'),
                 ('',False,'')]

    #Create Table
    table_data = []
    for item in Attachments:
        label = item.name
        this_url = reverse('DB:design_item_detail', args=[Item.id])
        edit_url = reverse('DB:edit', args=['Design_Object_Attachment', item.id])
        del_url = reverse('DB:delete', args=['Design_Object_Attachment', item.id])
        html = format_html('<a href="{1}?cont={0}">edit</a><br><a href="{2}?cont={0}">delete</a>', this_url, edit_url, del_url)
        table_data.append([[False, format_data_hover(item, label)],
                          [False, item.date.strftime('%B %d, %Y')],
                          [False, newlines(item.notes)],
                          [False, html]])
    table = Table(table_head, table_data)

    #Prepare html
    context = RequestContext(request,{'table':table,
                             'datatables':datatables,
                             'design_item_id':Item.id,
                             'design_item_name':Item.name}).flatten()
    return render(request, 'sample_database/details_design_item.html', context)

def newSample(request):
    error = False
    if request.method=='POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user
            sample.save()
            return redirect('DB:sample', sampleID = sample.id)
        else:
            error = form.errors
    form=SampleForm()
    form.fields["owner"].queryset = User.objects.filter(is_staff=True).order_by('first_name')
    context = RequestContext(request,{'form':form,
                                      'error':error,}).flatten()
    return render(request,'sample_database/new_sample.html',context)

def sample(request, sampleID):
    #Init
    order_by = request.GET.get('order', 'name')
    sample = Sample.objects.get(id = sampleID)
    title=Title([(reverse('DB:home'),'Home')],sample.name)

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
    new_piece_url = reverse('DB:new_piece', args=[sample.id])
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
        table_data.append([[reverse('DB:piece', args=[sample.id, piece.id]), format_html('<span data-tooltip class="has-tip-top" data-options="disable_for_touch:true" title="{0}">{1}</span>',map,piece.name)],
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
                             'sample':sample}).flatten()
    return render(request,'sample_database/sample.html',context)

def newPiece(request, sampleID):
    error = False
    sample = Sample.objects.get(id = sampleID)
    if request.method=='POST':
        form = PieceForm(request.POST,instance=Piece(sample=sample))
        if form.is_valid():
            piece = form.save()
            create = piece.action_set.get(action_type__name = 'Created')
            return redirect('DB:action_details', sample.id, piece.id, create.id)
        else:
            error = form.errors
    form=PieceForm()
    context = RequestContext(request,{'error':error,
                                      'sample':sample,
                                      'form':form,
                                      }).flatten()
    return render(request,'sample_database/new_piece.html',context)

def piece(request, sampleID, pieceID):
    #Init
    order_by = request.GET.get('order', 'date')
    s = Sample.objects.get(id = sampleID)
    p = s.piece_set.get(id = pieceID)
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample', args=[s.id]), s.name)], p.name)
    #Prepare Data
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
        table_data.append([[reverse('DB:action_details', args=[s.id, p.id, action.id]), label],
                          [False,action.date.strftime('%B %d, %Y %I:%M %p')],
                          [False,newlines(action.notes)],
                          [False,html]])
    table=Table(table_head,table_data)
    #Prepare html
    context = RequestContext(request,{'title':title,
                             'table':table,
                             'piece':p,
                             'datatables':datatables,
                             'sample':s}).flatten()
    return render(request,'sample_database/piece.html',context)

def actionDetails(request, sampleID, pieceID, actionID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(id = sampleID)
    p = s.piece_set.get(id = pieceID)
    a = Action.objects.get(id=actionID)
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample', args=[s.id]), s.name),
                 (reverse('DB:piece', args=[s.id, p.id]), p.name)],
                a.action_type.name+' ('+a.date.strftime('%B %d, %Y %I:%M %p')+')')
    error=None
    #Prepare Data
    EnabledParams = Action_Type.objects.get(id = a.action_type.id).params.all()
    params = Param_Value_Action.objects.filter(action = a).filter(param__in = EnabledParams).order_by('param__name')
    field_names=[el.param.name for el in params]
    field_names.append('Notes')
    field_data=[el.value for el in params]
    field_data.append(newlines(a.notes))
    fields=zip(field_names, field_data)
    #On POST
    if request.method == 'POST':
        #Need to validate form to get data_type; then validate for real
        form = GeneralDataForm([], request.POST)
        form.is_valid()
        data_type = Data_Type.objects.get(id = form.cleaned_data['data_type'].id)
        params = data_type.params.all()

        #Generate form for data_type as determined above then actually validate
        form = GeneralDataForm(params, request.POST, request.FILES)
        if form.is_valid():
            new_data=General(data_type=data_type,
                             image_file=form.cleaned_data['image_file'],
                             raw_data=form.cleaned_data['raw_data'],
                             notes=form.cleaned_data['notes'],
                             xmin=form.cleaned_data['xmin'],
                             xmax=form.cleaned_data['xmax'],
                             ymin=form.cleaned_data['ymin'],
                             ymax=form.cleaned_data['ymax'],
                             parent=a)
            new_data.save()
            
            for param in params:
                v = form.cleaned_data['{} ({:d})'.format(param.name, param.id)]
                param_value = Param_Value_Data(param = param, data = new_data, value = v)
                param_value.save()
        else:
            error = form.errors
    #Prepare Table
    data= a.general_set.order_by(order_by)
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
        table_data.append([[reverse('DB:general_details', args=[s.id, p.id, dat.id]), format_data_hover(dat,dat.data_type.name)],
                           [False,dat.date.strftime('%B %d, %I:%M %p')],
                           [False,newlines(dat.notes)],
                           [False,html]])
    table=Table(table_head,table_data)
    #Prepare Form
    form = []
    for type in data_types:
        f_temp = GeneralDataForm(type.params.all(), initial={'data_type':type})
        form.append([type.id, f_temp])
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
                             'add_zip':True}).flatten()
    return render(request,'sample_database/Modal_form.html',context)

def generalDetails(request, sampleID, pieceID, generalID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(id = sampleID)
    p = s.piece_set.get(id = pieceID)
    g = General.objects.get(id=generalID)
    a = g.parent
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample', args=[s.id]), s.name),
                 (reverse('DB:piece', args=[s.id, p.id]), p.name),
                 (reverse('DB:action_details', args=[s.id, p.id, a.id]),a.action_type.name+' ('+a.date.strftime('%B %d, %Y')+')')],
                g.data_type.name+' ('+g.date.strftime('%I:%M %p')+')')
    error=None
    #Prepare Data
    EnabledParams = Data_Type.objects.get(id = g.data_type.id).params.all()
    params = Param_Value_Data.objects.filter(data = g).filter(param__in = EnabledParams).order_by('param__name')
    field_names=[el.param.name for el in params]
    field_names+=['xmin','xmax','ymin','ymax','Notes']
    field_data=[el.value for el in params]
    field_data+=[g.xmin,g.xmax,g.ymin,g.ymax,newlines(g.notes)]
    fields=zip(field_names, field_data)
    #On POST
    if request.method=='POST':
        form=LocalDataForm([],request.POST,request.FILES)
        form.is_valid()
        data_type = Data_Type.objects.get(id = form.cleaned_data['data_type'].id)
        params = data_type.params.all()

        form=LocalDataForm(params, request.POST, request.FILES)
        if form.is_valid():
            new_data=Local(data_type=data_type,
                             image_file=form.cleaned_data['image_file'],
                             raw_data=form.cleaned_data['raw_data'],
                             notes=form.cleaned_data['notes'],
                             x=form.cleaned_data['x'],
                             y=form.cleaned_data['y'],
                             parent=g)
            new_data.save()
            
            for param in params:
                v = form.cleaned_data['{} ({:d})'.format(param.name, param.id)]
                param_value = Param_Value_Data(param = param, data = new_data, value = v)
                param_value.save()
        else:
            error=form.errors
    #Prepare Table
    data= g.local_set.order_by(order_by)
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
        table_data.append([[reverse('DB:local_details', args=[s.id, p.id, dat.id]), format_data_hover(dat, dat.data_type.name)],
                           [False,dat.date.strftime('%I:%M %p')],
                           [False,newlines(dat.notes)],
                           [False,html]])
    table=Table(table_head,table_data)
    #Prepare Form
    form = []
    for type in data_types:
        f_temp = LocalDataForm(type.params.all(), initial={'data_type':type})
        form.append([type.id, f_temp])

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
                             'obj':g}).flatten()
    return render(request,'sample_database/Modal_form.html',context)

def localDetails(request, sampleID, pieceID, localID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(id = sampleID)
    p = s.piece_set.get(id = pieceID)
    l = Local.objects.get(id=localID)
    g = l.parent
    a = g.parent
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample', args=[s.id]), s.name),
                 (reverse('DB:piece', args=[s.id, p.id]), p.name),
                 (reverse('DB:action_details',args=[s.id, p.id, a.id]),a.action_type.name+' ('+a.date.strftime('%B %d, %Y')+')'),
                 (reverse('DB:general_details',args=[s.id, p.id, g.id]),g.data_type.name+' ('+g.date.strftime('%I:%M %p')+')')],
                l.data_type.name)
    error=None
    #Prepare Data
    EnabledParams = Data_Type.objects.get(id = l.data_type.id).params.all()
    params = Param_Value_Data.objects.filter(data = l).filter(param__in = EnabledParams).order_by('param__name')
    field_names=[el.param.name for el in params]
    field_names+=['x','y','Notes']
    field_data=[el.value for el in params]
    field_data+=[l.x, l.y, newlines(l.notes)]
    fields=zip(field_names, field_data)
    #On POST
    if request.method=='POST':
        form=AttachmentForm([],request.POST,request.FILES)
        form.is_valid()
        data_type = Data_Type.objects.get(id = form.cleaned_data['data_type'].id)
        params = data_type.params.all()
        
        form = AttachmentForm(params, request.POST, request.FILES)
        if form.is_valid():
            new_data=Local_Attachment(data_type=data_type,
                           image_file=form.cleaned_data['image_file'],
                           raw_data=form.cleaned_data['raw_data'],
                           notes=form.cleaned_data['notes'],
                           parent=l)
            new_data.save()

            for param in params:
                v = form.cleaned_data['{} ({:d})'.format(param.name, param.id)]
                param_value = Param_Value_Data(param = param, data = new_data, value = v)
                param_value.save()
        else:
            error=form.errors
    #Prepare Table 
    data= l.local_attachment_set.order_by(order_by)
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
        table_data.append([[reverse('DB:attach_details', args=[s.id, p.id, dat.id]), format_data_hover(dat,dat.data_type.name)],
                           [False,dat.date.strftime('%B %d, %Y')],
                           [False,newlines(dat.notes)],
                           [False,html]])
    table=Table(table_head,table_data)
    #Prepare Form
    form=[]
    for type in data_types:
        f_temp = AttachmentForm(type.params.all(), initial={'data_type':type})
        form.append([type.id, f_temp])

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
                             'obj':l}).flatten()
    return render(request,'sample_database/Modal_form.html',context)

def attachDetails(request, sampleID, pieceID, attachID):
    #Init
    order_by = request.GET.get('order', 'date')
    data_types=Data_Type.objects.all()
    s = Sample.objects.get(id = sampleID)
    p = s.piece_set.get(id = pieceID)
    att=Local_Attachment.objects.get(id=attachID)
    l = att.parent
    g = l.parent
    a = g.parent
    title=Title([(reverse('DB:home'),'Home'),
                 (reverse('DB:sample', args=[s.id]), s.name),
                 (reverse('DB:piece', args=[s.id, p.id]), p.name),
                 (reverse('DB:action_details', args=[s.id, p.id, a.id]), a.action_type.name+' ('+a.date.strftime('%B %d, %Y')+')'),
                 (reverse('DB:general_details', args=[s.id, p.id, g.id]), g.data_type.name+' ('+g.date.strftime('%B %d, %Y')+')'),
                 (reverse('DB:local_details', args=[s.id, p.id, l.id]), l.data_type.name+' ('+l.date.strftime('%B %d, %Y')+')')],
                att.data_type.name+' ('+att.date.strftime('%B %d, %Y')+')')
    #Prepare Data
    EnabledParams = Data_Type.objects.get(id = att.data_type.id).params.all()
    params = Param_Value_Data.objects.filter(data = att).filter(param__in = EnabledParams).order_by('param__name')
    field_names=[el.param.name for el in params]
    field_names+=['Notes']
    field_data=[el.value for el in params]
    field_data+=[newlines(att.notes)]
    fields=zip(field_names, field_data)

    #Prepare html
    context = RequestContext(request,{'title':title,
                             'fields':fields,
                             'raw':att.raw_data,
                             'file':att.image_file,
                             'obj':att}).flatten()
    return render(request,'sample_database/Modal_form.html',context)

def newAction(request,action_type):
    error=False
    a_type = Action_Type.objects.get(name=action_type)
    params = a_type.params.all()
    if request.method=='POST':
        form = ActionForm(params, request.POST)
        if form.is_valid():
            pieces=[]
            for sample in Sample.objects.all():
                if len(sample.piece_set.all()) > 0:
                    pieces += form.cleaned_data[sample.name]
            new_action=Action(action_type=a_type,
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
                context = RequestContext(request,{'error':error,'form':form,'a_type':a_type}).flatten()
                return render(request,'sample_database/new_action.html',context)
            for p in params:
                v = form.cleaned_data['{} ({:d})'.format(p.name, p.id)]
                param_value = Param_Value_Action(param = p, action = new_action, value = v)
                param_value.save()
            return redirect('DB:home')
        else:
            error = form.errors
    else:
        form=ActionForm(params)
    # Split form up to properties and samples
    form_props = []
    form_samples = []
    for field in form:
        temp = {'errors':field.errors,
                'help_text':field.help_text,
                'label_tag':field.label_tag(),
                'field':field.__str__()}
        if field.help_text == 'sample':
            form_samples.append(temp)
        else:
            form_props.append(temp)
    context = RequestContext(request,{'error':error,'form_props':form_props,'form_samples':form_samples,'a_type':a_type}).flatten()
    return render(request,'sample_database/new_action.html',context)

def edit(request,type,id):
    prompt = ''
    action_types = Action_Type.objects.filter(~Q(name='Created'))
    editable = ['Piece','Sample','Action','General','Local','Local_Attachment','Design','Design_Item','Design_Object_Attachment']
    error = False
    obj = False
    form = ''
    if type not in editable:
        error= "%s not editable or does not exist"%type
    else:
        obj = eval(type + ".objects.get(id=%s)"%id)
        obj.last_modified_by = request.user
        error = isPOST(request, eval("edit_%s"%type), obj)
        form = eval("edit_%s(instance=obj)"%type)
        
        if type == 'Sample':
            form.fields["owner"].queryset = User.objects.filter(is_staff=True).order_by('first_name')
        
        if not error and request.POST:
            continue_url = request.GET.get('cont')
            if continue_url:
                return redirect(continue_url)
            try: return redirect(obj.url())
            except: pass  # If not url method, just return this form
    context = RequestContext(request,{'obj':obj,
                                      'error':error,
                                      'type':type.replace("_", " "),
                                      'caller':'Edit',
                                      'prompt':prompt,
                                      'edit_form':form}).flatten()
    return render(request,'sample_database/edit.html',context)

def delete(request,type,id):
    error=False
    obj=False
    form=''
    prompt=''
    editable=['Sample','Piece','Action','General','Local','Local_Attachment','Design','Design_Item','Design_Object_Attachment']
    caller='Delete'
    if type not in editable:
        error = "%s not editable or does not exist"%type
    if type=='Action' or type=='Sample' or type=='Design' or type=='Design_Item' or type=='Design_Object_Attachment':
        if type=='Action':name= eval(type+".objects.get(id=%s)"%id).action_type.name
        if type=='Sample' or type=='Design' or type=='Design_Item' or type=='Design_Object_Attachment':name= eval(type+".objects.get(id=%s)"%id).name
        if name=='None' or name=='Created':
            error="%s %s is not deletable"%(type,name)
    if not error:
        obj=eval(type+".objects.get(id=%s)"%id)
        if request.POST:
            try:
                obj.delete()
            except models.ProtectedError:
                error="%s %s is not deletable since it is in usage by another object"%(type,name)
                context = RequestContext(request,{'obj':obj,
                                      'error':error,
                                      'type':type.replace("_", " "),
                                      'caller':caller,
                                      'prompt':SafeString(prompt)}).flatten()
                return render(request,'sample_database/edit.html',context)


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
                                      'type':type.replace("_", " "),
                                      'caller':caller,
                                      'prompt':SafeString(prompt)}).flatten()
    return render(request,'sample_database/edit.html',context)

def upload_zip(request, attachID, parent_id):
    error = False
    parent = Action.objects.get(id = parent_id)
    type = Data_Type.objects.get(id = attachID)
    prompt = 'Filenames will go to notes unless a txt file is supplied. The txt file needs <b>one line per file!</b>'
    if request.method == 'POST':
        form = ZipForm(type.params.all(), request.POST, request.FILES)
        if form.is_valid():
            NEXT = form.cleaned_data['referrer']
            out, error = form.save(parent, type)
            if not error:
                return redirect(NEXT)
            else:
                error = out
        else:
            error = form.errors
    NEXT = request.GET.get('next','DB:home')
    form = ZipForm(type.params.all(), initial={'referrer':NEXT})
    context = RequestContext(request, {'parent':parent,
                                      'type':type,
                                      'error':error,
                                      'form':form,
                                      'prompt':SafeString(prompt)}).flatten()
    return render(request,'sample_database/upload_zip.html',context)

