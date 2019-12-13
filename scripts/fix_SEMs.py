import image_util
import sys, os, datetime
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
from django.db import models
from sample_database.models import *
import inspect

SEMs = General.objects.filter(data_type__name='SEM')
print len(SEMs)

for sem in SEMs:
    name = os.path.splitext(sem.image_file.name)[0]
    path = sem.image_file.path
    path_out = image_util.to_PNG(path,delete=False)
    sem.image_file = name+'.png'
    sem.save()
