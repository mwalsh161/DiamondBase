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
    field_names=dat.data_type.field_names.split('\r\n')
    i=pos(lambda a: prop.lower() in a.lower(),field_names)
    if i==None:
        raise Exception("No property named %s in %s"%(prop, dat.data_type.name))
    field_value=dat.fields.split('\r\n')
    return cast(field_value[i])

if __name__ == '__main__':
    piece_name=sys.argv[1]
    between=False
    if len(sys.argv)==4:
        between=True
        low=sys.argv[2]
        high=sys.argv[3]
    resonances=Local_Attachment.objects.filter(data_type__name='Resonance',parent__parent__parent__pieces__name=piece_name)
    for res in resonances:
        if between:
            if get('wavelength',res)>low and get('wavelength',res)<high:
                print 'Wavelength',get('wavelength',res)
                print 'Q',get('Q',res)
                print res.parent.parent.parent.pieces.all()
                print res.parent.parent.notes
                print '________________________________________________________________________'
        
        else:
            print 'Wavelength',get('wavelength',res)
            print 'Q',get('Q',res)
            print res.parent.parent.parent.pieces.all()
            print res.parent.parent.notes
            print '________________________________________________________________________'
