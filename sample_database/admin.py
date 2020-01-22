from sample_database.models import *
from django.contrib import admin
#from django.core import urlresolvers
from django.contrib.auth.models import User

#Hide slug fields

class NoSlug(admin.ModelAdmin):
    readonly_fields=['slug']

class ProjectAdmin(NoSlug):
    def get_form(self,request, obj=None, **kwargs):
        form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['supervisor'].queryset = User.objects.filter(is_staff=True).order_by('first_name')
        return form

class SampleAdmin(NoSlug):
    def get_form(self,request, obj=None, **kwargs):
        form = super(SampleAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['owner'].queryset = User.objects.filter(is_staff=True).order_by('first_name')
        form.base_fields['last_modified_by'].queryset = User.objects.filter(is_staff=True).order_by('first_name')
        return form

admin.site.register(Design)
admin.site.register(Action_Type,NoSlug)
admin.site.register(Data_Type,NoSlug)
admin.site.register(Piece,NoSlug)
admin.site.register(Sample,SampleAdmin)
admin.site.register(Location,NoSlug)
admin.site.register(Substrate,NoSlug)
admin.site.register(Project,ProjectAdmin)
