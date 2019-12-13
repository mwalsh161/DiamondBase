from django.conf import settings
from sample_database.models import *
from django.db.models import Q

def action_types(request):
    actions=Action_Type.objects.filter(~Q(name='Created')).order_by('name')
    return {'action_types':actions}

def lab_name(request):
    return {'LAB_NAME':settings.LABNAME}