import sys, os, datetime, json
import urllib as url
sys.path.insert(0,'/home/diamondbase/DiamondBase/DiamondBase')
sys.path.insert(1,'/home/diamondbase/DiamondBase')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
from django.db import models
from django.utils import timezone
import django
from sample_database.models import Design, Piece, Sample
from sample_database.models import Action_Type, Action
from sample_database.models import Data_Type, General, Local, Local_Attachment
from django.contrib.auth.models import User
from ip_tracker.models import *
import inspect

django.setup()

DELIM = '@'

def error(msg):
    return 'Error in '+inspect.stack()[1][3]+': '+msg

def Help():
    out = '''Provides SSH interface to diamond database.
__________________________________________________________________
Syntax:
get_samples [n most recent] -> ID|sampleName (one per line)
qet_diamonds sampleID -> ID|diamondName (one per line)
get_experimentIDs diamondID -> ID|date (one per line)
get_data_types -> ID|dataType (one per line)
new_experiment diamondID1,ID2,ID3 "notes" -> experimentID
add_general experimentID DataTypeID "file_path|raw_path|xmin|xmax|ymin|ymax|field1|field2|...|notes" -> generalID
add_local generalID DataTypeID "file_path|raw_path|x|y|field1|field2|...|notes" -> localID
add_attachment localID DataTypeID "file_path|raw_path|field1|field2|...|notes" -> attachID
ip_update "name" "ip" -> status
ip_lookup "name" -> "ip"
custom_query "python code" -> string/list (the variable "out" is what is returned as a string.  If it is a list, it will separate list items by newlines). Note json module is loaded in this file.

Notes:
Example django query code:  Data_Type.objects.get(name='NV').id [MUST USE SINGLE QUOTES]
The last field in an add_data needs to be url encoded (utf-8)
The global DELIM is used as a delimiter on a given line.
FILE PATH MUST BE WITHIN SCOPE OF SERVER if you want to be able to download it.
        
Michael Walsh
mpwalsh@mit.edu
April 7, 2014
'''
    return out

PATH = os.path.dirname(os.path.abspath(__file__))

def main(argv):
    with open(os.path.join(PATH,'temp.txt'), 'w') as f:
        f.write(str(argv)+'\n')
    todo=argv.pop(0)   #pop(0) returns and removes first element of list
    if todo=='get_diamonds':
        return get_diamonds(argv)
    elif todo=='get_delim':
        return DELIM
    elif todo=='get_samples':
        return get_samples(argv)
    elif todo=='get_experimentIDs':
        return get_experimentIDs(argv)
    elif todo=='new_experiment':
        return new_experiment(argv)
    elif todo=='get_data_types':
        return get_data_types(argv)
    elif todo=='add_general':
        return add_data('General',argv)
    elif todo=='add_local':
        return add_data('Local',argv)
    elif todo=='add_attachment':
        return add_data('Attach',argv)
    elif todo=='ip_update':
        return ip_update(argv)
    elif todo=='ip_lookup':
        return ip_lookup(argv)
    elif todo=='custom_query':
        return custom_query(argv)
    else:
        return error('no such command! Run with no args for help')

def ip_lookup(argv):
    if len(argv)!=1:
        return error('expected one argument')
    NAME = argv[0]
    try:
        computer=Computer.objects.get(name=NAME)
    except:
        return error('Computer by name of "%s" does not exist.'%NAME)
    return computer.ip

def ip_update(argv):
    if len(argv)!=2:
        return error('expected two arguments')
    NAME,IP=argv
    try:
        computer=Computer.objects.get(name=NAME)
    except Computer.DoesNotExist:
        computer=Computer(name=NAME)
    if IP == 'Error' or IP == 'Shutting Down':
        computer.notes = IP
    else:
        computer.ip = IP
        computer.notes = ''
    computer.save()
    return True

def get_samples(argv):
    if len(argv)>1:
        return error('too many arguments')
    n=None
    if len(argv)==1:
            n=argv[0]
    samples=Sample.objects.all().order_by('-date_created')[0:n]
    out=''
    for sample in samples:
        out+=str(sample.id)+DELIM+sample.name+'\n'
    return out[0:-1]

def get_diamonds(argv):
    if len(argv)!=1:
        return error('wrong number of arguments')
    sampleID = argv[0]
    sample=Sample.objects.get(id=sampleID)
    out=''
    for piece in sample.piece_set.order_by('-date_created'):
        out+=str(piece.id)+DELIM+piece.name+'\n'
    return out[0:-1]

def get_experimentIDs(argv):
    if len(argv)!=1:
        return error('wrong number of arguments')
    diamondID=argv[0]
    diamond=Piece.objects.get(id=diamondID)
    out=''
    for exp in diamond.action_set.filter(action_type__name='Experiment'):
        out+=str(exp.id)+DELIM+exp.date.strftime('%B %d, %Y')+'\n'
    return out[0:-1]

def new_experiment(argv):
    if len(argv)>2:
        return error('wrong number of arguments')
    diamondID=argv[0]
    for i in diamondID.split(','):
        try:
            ID=int(i)
        except:
            return error('incorrect ID list - aborted creation')
    if len(argv)>1:
        Notes=argv[1]
    else: Notes=''
    type=Action_Type.objects.get(name='Experiment')
    new_action=Action(action_type=type,
                      notes=Notes,
                      owner=User.objects.get(username='SSH'),
                      date=timezone.now())
    new_action.save()
    for i in diamondID.split(','):
        ID=int(i)
        diamond=Piece.objects.get(id=ID)
        new_action.pieces.add(diamond)
    return new_action.id

def get_data_types(argv):
    if len(argv)>0:
        return error('too many arguments')
    out=''
    for dat in Data_Type.objects.all():
        out+=str(dat.id)+DELIM+dat.name+'\n'
    return out[0:-1]

#Could combine the "add_*" to one function if you want to use eval, but that is not secure
def add_data(type,argv):
    if len(argv)!=3:
        return error('wrong number of arguments')
    [parentID,dataTypeID,data]=argv
    data = url.unquote_plus(data)
    if type=='General': i = 4  #xmin,xmax,ymin,ymax
    elif type=='Local': i = 2  #x,y
    elif type=='Attach':i = 0
    else: return error('wrong data type')
    dataType=Data_Type.objects.get(id=dataTypeID)
    fields=validate(data,dataType,i)
    if not fields[0]:
        return error('wrong number of fields for %s. Expected %i, received %i.'%(dataType.name,fields[2],fields[1]))
    f=''
    for field in fields[i+2:-1]:   #Exclude file, raw_file, type stuff, notes
        f+=field+'\r\n'
    f=f[0:-1]  #Remove last endline
    if type=='General':
        [err,parent]=get_obj(Action,parentID)
        if err: return parent
        new_data = General(data_type=dataType,
                         fields=f,
                         image_file=fields[0],
                         raw_data=fields[1],
                         xmin=fields[2],
                         xmax=fields[3],
                         ymin=fields[4],
                         ymax=fields[5],
                         notes=fields[-1],
                         parent=parent,
                         date=timezone.now())
    elif type=='Local':
        [err,parent]=get_obj(General,parentID)
        if err: return parent
        new_data = Local(data_type=dataType,
                           fields=f,
                           image_file=fields[0],
                           raw_data=fields[1],
                           x=float(fields[2]),
                           y=float(fields[3]),
                           notes=fields[-1],
                           parent=parent,
                           date=timezone.now())
    elif type=='Attach':
        [err,parent]=get_obj(Local,parentID)
        if err: return parent
        new_data = Local_Attachment(data_type=dataType,
                           fields=f,
                           image_file=fields[0],
                           raw_data=fields[1],
                           notes=fields[-1],
                           parent=parent,
                           date=timezone.now())
    new_data.save()
    return new_data.id

def custom_query(argv):
    code = str(url.unquote_plus(argv[0])).decode('utf-8')
    try:
        exec(code)
    except Exception as err:
        out = error(str(err))
    #If out is a list, separate by new lines
    if type(out)==list:
        temp = ''
        for item in out:
            temp+=str(item)+'\n'
        out = temp[0:-1]
    return out

def validate(data,dataType,extra):
    fields = str(dataType.field_names).splitlines()
    length = len([el for el in fields if len(el)>0])
    data_length=len(data.split(DELIM)[2:-1])  #leave off file,notes
    if data_length-extra==length:
        return data.split(DELIM)
    return (False,data_length,length+extra)

def get_obj(data,ID):
    try:
        return False,data.objects.get(id=ID)
    except:
        return True,error('does not exist')

if __name__ == '__main__':
    if len(sys.argv)>1:
        print main(sys.argv[1:])
    else:
        print Help()
    sys.exit(0)
