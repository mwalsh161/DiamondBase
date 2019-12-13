from django import forms
from django.forms import ModelForm
from ip_tracker.models import *

class ComputerForm(ModelForm):
    class Meta:
        model=Computer
        exclude=['date_modified']
