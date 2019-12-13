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

def gather_res(experiment):
    data = {}
    generals=experiment.general_set.filter(data_type__name='Confocal')
    for item in generals:
        locals=item.local_set.filter(data_type__name='Spectrum')
        for loc in locals:
            resonances=loc.local_attachment_set.filter(data_type__name='Resonance')
            for res in resonances:
                if item.notes not in data.keys():
                    data[item.notes]=[[],[]]
                data[item.notes][0].append(get('Wavelength',res,float))
                data[item.notes][1].append(get('Q',res,float))

    return data

piece = Piece.objects.get(name='EGM5a')
before = piece.action_set.get(date__year=2014,date__month=7,date__day=14,action_type__name='Experiment')
after = piece.action_set.get(date__year=2014,date__month=7,date__day=15,action_type__name='Experiment')
before_dat=gather_res(before)
after_dat=gather_res(after)

def MATLAB(region):
    before=str(before_dat[region][0])
    after =str(after_dat[region][0])
    out = "plot(1,%s,'.',2,%s,'.','markersize',25);title(%s)"%(before,after,region)
    return out
