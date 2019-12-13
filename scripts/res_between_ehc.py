import sys, os, datetime
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
from django.db import models
from sample_database.models import *
import inspect
import numpy as np

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

resonances=Local_Attachment.objects.filter(data_type__name='Resonance')

if __name__ == '__main__':
    low=sys.argv[1]
    high=sys.argv[2]
    Qlist = np.array([])
    NotesList = np.array([])
    PieceNameList = np.array([])
    for res in resonances:
        Qlist = np.append(Qlist,float(get('Q',res)))
	PieceNameList = np.append(PieceNameList,res.parent.parent.parent.pieces.all())
	NotesList = np.append(NotesList,res.parent.parent.notes)
	if get('Wavelength',res,float)<640 and get('Wavelength',res,float)>625:
            print 'Wavelength',get('wavelength',res)
            print 'Q',get('Q',res)
            print res.parent.parent.parent.pieces.all()
            print res.parent.parent.notes
            print '________________________________________________________________________'
    print Qlist
    print np.mean(Qlist)
    maxindex = np.argmax(Qlist)
    print maxindex
    print np.max(Qlist)
    print np.std(Qlist)
    print PieceNameList[maxindex]
    print NotesList[maxindex]
