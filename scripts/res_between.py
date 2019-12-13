'''Note - only taking first 4 characters of notes for confocal and first character for spectrum'''


import sys, os, datetime
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
from django.db import models
from sample_database.models import *
import inspect

def find(f,seq):
    output=[]
    for item in seq:
        if f(item):
            output.append(item)
    return output

def pos(f,seq):
    i=0
    for item in seq:
        if f(item):
            return i
        i+=1

def get(prop,dat,cast=str):
    field_names=dat.data_type.field_names.splitlines()
    i=pos(lambda a: prop.lower() in a.lower(),field_names)
    if i==None:
        raise Exception("No property named %s in %s"%(prop, dat.data_type.name))
    field_value=dat.fields.splitlines()
    return cast(field_value[i])

if __name__ == '__main__':
    month,day,year=sys.argv[1].split('/')
    low=float(sys.argv[2])
    high=float(sys.argv[3])
    have=[]
    resonances=Local_Attachment.objects.filter(data_type__name='Resonance',parent__parent__parent__date__year=year,parent__parent__parent__date__month=month,parent__parent__parent__date__day=day)
    num=0
    for res in resonances:
        if get('Wavelength',res,float) > low and get('Wavelength',res,float) < high:
            if res.parent.parent.notes[0:4] not in have:
                have.append(res.parent.parent.notes[0:4])
                num+=1
                print 'Wavelength',get('wavelength',res)
                print 'Q',get('Q',res)
                print 'Contrast',get('Contrast',res)
                print "%s (%s)"%(res.parent.parent.notes[0:4],res.parent.notes[0])
                print '________________________________________________________________________'
    print num
