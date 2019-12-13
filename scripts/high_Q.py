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

if __name__ == '__main__':
    piece_name=sys.argv[1]
    q_threshold=float(sys.argv[2])
    resonances=Local_Attachment.objects.filter(data_type__name='Resonance',parent__parent__parent__pieces__name=piece_name)
    for res in resonances:
        if res.get('Q',float) > q_threshold:
            print 'Wavelength',res.get('wavelength')
            print 'Q',res.get('Q')
            print res.parent.parent.parent.pieces.all()
            print res.parent.parent.notes
            print '________________________________________________________________________'
