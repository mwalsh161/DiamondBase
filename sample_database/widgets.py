from django import forms
from django.utils.safestring import mark_safe

class ModularMultipleChoice(forms.CheckboxSelectMultiple):
    def render(self,name,value,attrs=None,renderer=None):
        html=super(ModularMultipleChoice,self).render(name, value, attrs, renderer)
        #Use javascript to make each one collapsable and select-all(able)
        
        return mark_safe(html)

