import datetime, os
from django.utils import timezone
import my_zip
import image_util as im
from django import forms
from django.forms import ModelForm
from django.conf import settings
from sample_database.models import *
from sample_database.widgets import *

class edit_Action(ModelForm):
    class Meta:
        model=Action
        exclude=['action_type','pieces','last_modified','last_modified_by']
class edit_General(ModelForm):
    class Meta:
        model=General
        exclude=['data_type','image_file','raw_data','parent']
class edit_Local(ModelForm):
    class Meta:
        model=Local
        exclude=['data_type','image_file','raw_data','parent']
class edit_Local_Attachment(ModelForm):
    class Meta:
        model=Local_Attachment
        exclude=['data_type','image_file','raw_data','parent']
class edit_Sample(ModelForm):
    class Meta:
        model=Sample
        exclude=['slug','name','date_created','last_modified_by','last_modified']
    def __init__(self, *args, **kwargs):
        super(edit_Sample, self).__init__(*args, **kwargs)   
        self.fields['location'].queryset = Location.objects.order_by('name')
        self.fields['substrate'].queryset = Substrate.objects.order_by('name')
class edit_Piece(ModelForm):
    class Meta:
        model=Piece
        exclude=['slug','name']

class DesignForm(ModelForm):
    class Meta:
        model=Design
        fields=['name','design_items','vector_file','image_file','notes']

class MapForm(ModelForm):
    class Meta:
        model=SampleMap
        exclude=['sample']

class SampleForm(ModelForm):
    class Meta:
        model=Sample
        exclude=['slug','last_modified_by']

    def __init__(self, *args, **kwargs):
        super(SampleForm, self).__init__(*args, **kwargs)   
        self.fields['location'].queryset = Location.objects.order_by('name')
        self.fields['substrate'].queryset = Substrate.objects.order_by('name')

    def clean_name(self):
        name = self.cleaned_data['name']
        samples = Sample.objects.filter(name=name)
        if samples.count():
            raise forms.ValidationError('Sample already exists')
        return name

    def save(self,*args,**kwargs):
        instance = super(SampleForm,self).save(*args,**kwargs)
        instance.save()
        # Create two default side pieces
        des = Design.objects.get(name='Bulk Diamond')
        small = Piece(sample=instance,name='smallside',design=des).save()
        big = Piece(sample=instance,name='bigside',design=des).save()
        return instance

class PieceForm(ModelForm):
    notes=forms.CharField(widget=forms.Textarea,required=False)
    class Meta:
        model=Piece
        fields=['name','design','parent']

    def init(self,*args,**kwargs):
        super(PieceForm,self).__init__(*args,**kwargs)
        self.fields.keyOrder=['name','design','notes','parent']
    
class lostForm(ModelForm):
    class Meta:
        model=Piece
        fields=['gone']

class ActionForm(forms.Form):
    def __init__(self,fields, *args, **kwargs):
        super(ActionForm,self).__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.localtime(timezone.now())
        for field in fields:
            self.fields[field]=forms.CharField()
        for sample in Sample.objects.order_by('-id'):
            if sample.piece_set.count() > 0:
                self.fields[sample.name]=forms.ModelMultipleChoiceField(help_text='sample',widget=ModularMultipleChoice,queryset=sample.piece_set.filter(gone=False).order_by('-id'),required=False)
        self.fields.keyOrder=[el.name for el in Sample.objects.order_by('-id') if el.piece_set.count()>0]+fields+['date','notes']
    notes=forms.CharField(widget=forms.Textarea,required=False)
    date=forms.DateTimeField(required=True,initial=timezone.localtime(timezone.now()))

class DataForm(forms.Form):
    data_type=forms.ModelChoiceField(widget=forms.HiddenInput,queryset=Data_Type.objects.all())
    image_file=forms.FileField(required=False)
    raw_data=forms.FileField(required=False)
    notes=forms.CharField(widget=forms.Textarea,required=False)

#    def save(self, model_type, commit=True,*args,**kwargs):
#        data_type=self.cleaned_data['data_type']
#        fields=[self.cleaned_data[el] for el in data_type.field_names.splitlines() if len(el)>0]
#        fields = '\r\n'.join(fields)
#        if not self.instance:
#            self.instance=model_type()
#        for key in self.fields.keyOrder:
#            setattr(self.instance,key,self.cleaned_data[key])
#        new_data.fields = fields
#        new_data.save(commit,*args,**kwargs)
#        return self.instance

class GeneralDataForm(DataForm):
    def __init__(self,fields, *args, **kwargs):
        super(DataForm,self).__init__(*args, **kwargs)
        for field in fields:
            self.fields[field]=forms.CharField()
        self.fields.keyOrder=['data_type']+fields+['image_file','raw_data','xmin','xmax','ymin','ymax','notes']
    xmin=forms.FloatField(initial=0)
    xmax=forms.FloatField(initial=0)
    ymin=forms.FloatField(initial=0)
    ymax=forms.FloatField(initial=0)
    
class LocalDataForm(DataForm):
    def __init__(self,fields, *args, **kwargs):
        super(DataForm,self).__init__(*args, **kwargs)
        for field in fields:
            self.fields[field]=forms.CharField()
        self.fields.keyOrder=['data_type']+fields+['image_file','raw_data','x','y','notes']
    x=forms.FloatField()
    y=forms.FloatField()

class AttachmentForm(DataForm):
    def __init__(self,fields, *args, **kwargs):
        super(DataForm,self).__init__(*args, **kwargs)
        for field in fields:
            self.fields[field]=forms.CharField()
        self.fields.keyOrder=['data_type']+fields+['image_file','raw_data','notes']

class ZipForm(forms.Form):
    zip_file = forms.FileField(required=True)
    text_file = forms.FileField(required=False)
    referrer = forms.CharField(widget=forms.HiddenInput)
    
    def __init__(self,type,*args,**kwargs):
        super(ZipForm,self).__init__(*args, **kwargs)
        fields = [el for el in type.field_names.splitlines() if len(el)>0]
        for field in fields:
            self.fields[field]=forms.CharField()

    def clean_zip_file(self):
        EXTENTIONS = ['.png','.tif','.jpg','.tiff']
        zip_file = self.cleaned_data['zip_file']
        if my_zip.check_depth(zip_file)!=1:
            raise forms.ValidationError('Atleast one folder found (only select files to compress)')
        if not my_zip.check_extentions(zip_file,EXTENTIONS):
            raise forms.ValidationError('At least one file is not a supported image file %s'%str(EXTENTIONS))
        return zip_file

    def clean_text_file(self):
        text_file = self.cleaned_data['text_file']
        if text_file != None:
            name,ext = os.path.splitext(text_file.name)
            if ext.lower() != '.txt':
                raise forms.ValidationError('Must be txt file')
        return text_file

    def save(self,parent,type):
        error = False
        date = datetime.date.today().strftime('%m_%d_%Y')
        partial_path = os.path.join('diamond_base',type.name,date,parent.pieces.all()[0].name)
        path = os.path.join(settings.MEDIA_ROOT,partial_path)
        text_file = self.cleaned_data['text_file']
        zip_file = self.cleaned_data['zip_file']
        flist = my_zip.unzip(zip_file,path)
        new_data = []
        #Fromat fields for DB
        fields=''
        POST_fields=[el for el in type.field_names.splitlines() if len(el)>0]
        for POST_field in POST_fields:
            fields+=self.cleaned_data[POST_field]+'\r\n'
        if text_file != None:
            text_file = text_file.readlines()
            if len(text_file)!=len(flist):
                error = True
                for f in flist:
                    os.remove(f)
                return 'Text File has %i lines (should have %i)'%(len(text_file),len(flist)), error
        counter = 0
        for f in flist:   #Now save an instance for each
            filename = os.path.splitext(os.path.basename(f))[0]
            if text_file == None:
                NOTES = filename
            else:
                NOTES = text_file[counter].strip('\n')
            #Need to replace path with just the part after MEDIA_ROOT
            f = f.replace(settings.MEDIA_ROOT,'')
            d = General(data_type=type,
                        image_file=f,
                        fields=fields,
                        parent=parent,
                        notes=NOTES, xmin=0, ymin=0, xmax=0, ymax=0)
            counter += 1
            d.save()
            new_data.append(d)
        return new_data, error

'''
##UNDER CONSTRUCTION
class edit(forms.Form):
    def __init__(self,instance,*args,**kwargs):
        super(forms.Form,self).__init__(instance=instance,*args,**kwargs)
        field_names = [el for el in self.field_names.splitlines() if len(el)>0]
        fields = [el for el in self.fields.splitlines() if len(el)>0]
        for i in range(len( self.field_names)):
            field = field_names[i]
            value = fields[i]
            self.fields[field]=forms.CharField(intial=value)
        self.fields.keyOrder+=self.field_names
    def save(self,*args,**kwargs):
        field_names = [el for el in self.field_names.splitlines() if len(el)>0]
        fields = ''
        for name in field_names:
            fields+=self.cleaned_data[name]+'\r\n'
'''     
