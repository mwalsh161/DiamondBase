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
    wavelength = []
    Q = []
    contrast = []
    resonances=Local_Attachment.objects.filter(data_type__name='Resonance',parent__parent__parent__date__year=year,parent__parent__parent__date__month=month,parent__parent__parent__date__day=day)
    for res in resonances:
        wavelength.append(get('Wavelength',res,float))
        Q.append(get('Q',res,float))
        contrast.append(get('Contrast',res,float))
    print 'wavelength=%s'%str(wavelength)
    print 'Q=%s'%str(Q)
    print 'cont=%s'%str(contrast)
