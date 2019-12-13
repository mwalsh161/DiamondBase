import sys, os, datetime
sys.path.append('/home/diamondbase/DiamondBase')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
import django
django.setup()
from django.db import models
from sample_database.models import *
import inspect

types = {'EGM':Substrate.objects.get(name='Membrane EG'),
         'EG':Substrate.objects.get(name='Bulk EG'),
         'D':Substrate.objects.get(name='Bulk IIa'),
         'glass':Substrate.objects.get(name='Glass'),
         'SiC':Substrate.objects.get(name='SiC'),
         'Si':Substrate.objects.get(name='Silicon')}

if __name__ == '__main__':
    for sample in Sample.objects.all():
        name = sample.name
        if 'EGM' in name:
            sample.substrate = types['EGM']
        elif 'EG' in name:
            sample.substrate = types['EG']
        elif name[0]=='D':
            sample.substrate = types['D']
        elif 'glass' in name.lower():
            sample.substrate = types['glass']
        elif 'SiC' in name:
            sample.substrate = types['SiC']
        elif 'si' in name.lower() and not 'SI' in name:
            sample.substrate = types['Si']
        else:
            continue
        sample.save()
