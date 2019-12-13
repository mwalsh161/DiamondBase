import sys, os, datetime
sys.path.append('/home/diamondbase/DiamondBase')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
import django
django.setup()
from django.db import models
from sample_database.models import *
import inspect

implant = Action_Type.objects.get(name='Implantation')

candidates = []

LEARNED = {}
def math2num(val):
    # Interpret strings in scientific notation
    if val in LEARNED:
        return LEARNED[val]
    val = val.replace('x10','e')
    try:
        val = float(val)
        return val
    except:
        out = raw_input('Express "%s" scientific notation: '%val)
        out = math2num(out)
        LEARNED[val]=out
        return out

samples = Sample.objects.filter(name__contains='EG')
print 'Checking %i samples'%samples.count()
for s in samples:
    pieces = s.piece_set.all()
    if 'EGM' in s.name:
        continue
    if len(pieces) == 0:
        continue
    for p in pieces:
        actions = p.action_set.filter(action_type = implant)
        for action in actions:
            dose = math2num(action.get('Dosage'))
            if dose >= 10**10:
                if s != candidates:
                    candidates.append([s,dose])

for c in candidates:
    print '{:<30}{}'.format(c[0],c[1])
