import sys, os, datetime
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
from django.db import models
from django.conf import settings
from sample_database.models import Design, Action_Type, Data_Type, Sample

if len(Sample.objects.all())==0:
    print "Creating 'None' Sample"
    a = Sample(name='None',
               location = settings.LAB_NAME,
               notes = '''Use this for Pieces that don't have a "final" sample.''')
    a.save()

if len(Action_Type.objects.all())==0:
    #Create Action_Types
    print "Creating Action_Types"
    a = Action_Type(name='Implantation',
                   field_names='Energy (keV)\r\nDosage (#/cm^2)\r\nImplanted Ion')
    a.save()

    a = Action_Type(name='Anneal',
                   field_names='Recipe (Temp1,Time1;Temp2,Time2)\r\nPressure (mbar)')
    a.save()

    a = Action_Type(name='Experiment',
                   field_names='')
    a.save()

    a = Action_Type(name='Bake',
                   field_names='Temperature (C)\r\nDuration (min)\r\nPressure (mbar)\r\nGas')
    a.save()

    a = Action_Type(name='Etch',
                   field_names='Energy (keV)\r\nDosage (#/cm^2)\r\nIon')
    a.save()

    a = Action_Type(name='Acid Clean',
                   field_names='Acid(s)\r\nTemperature (C)\r\nDuration (min)')
    a.save()

    a = Action_Type(name='Created',
                   field_names='')
    a.save()

else:
    print 'ABORTING Action_Type - Seems to already be populated'

if len(Data_Type.objects.all())==0:
    #Create Data_Types
    print "Creating Data_Types"
    a = Data_Type(name='Resonant Excitation',
                   field_names='Red Power (nW)\r\nGreen Power (uW)')
    a.save()

    a = Data_Type(name='Confocal',
                   field_names='Laser Power (uW)')
    a.save()

    a = Data_Type(name='White Light',
                   field_names='')
    a.save()

    a = Data_Type(name='Spectrum',
                   field_names='Laser Power (uW)')
    a.save()

    a = Data_Type(name='Map File',
                   field_names='')
    a.save()

    a = Data_Type(name='Analysis File',
                   field_names='')
    a.save()

else: 
    print 'ABORTING Data_Type - Seems to already be populated'

if len(Design.objects.all())==0:
    #Create Designs
    print "Creating Designs"
    print "Don't forget to add files when this finishes!!"
    a = Design(name='Membrane',
               notes='No patterning',
               vector_file='',image_file='')
    a.save()

    a = Design(name='Bullseye',
               notes='',
               vector_file='',image_file='')
    a.save()

    a = Design(name='2D-PCC',
               notes='3 L3 (2 optimized for out coupling) and 1 M0',
               vector_file='',image_file='')
    a.save()

    a = Design(name='2D-PCC with implantation holes',
               notes='3 L3 (2 optimized for out coupling) and 1 M0',
               vector_file='',image_file='')
    a.save()

    a = Design(name='1D-PCC',
               notes='5 Ladders',
               vector_file='',image_file='')
    a.save()

    a = Design(name='Hybrid 1D and 2D',
               notes='No implantation holes',
               vector_file='',image_file='')
    a.save()

else:
    print 'ABORTING Designs - Seems to already be populated'

print 'Done'
