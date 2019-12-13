import sys, os, datetime
sys.path.append('/home/diamondbase/DiamondBase')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
import django
django.setup()
from django.db import models
from sample_database.models import *
import inspect

if __name__ == '__main__':
    not_annealed = []
    samples = Sample.objects.filter(name__contains='EG')
    for s in samples:
        pieces = s.piece_set.all()
        if len(pieces)==0:
            not_annealed.append(s)
        for p in pieces:
            if len(p.action_set.filter(action_type__name='Anneal'))==0:
                not_annealed.append(s)
                break
    for s in not_annealed:
        if 'EGM' not in s.name:
            print '%s (%i pieces)'%(s.name,len(s.piece_set.all()))
