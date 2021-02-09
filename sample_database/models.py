from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.utils import timezone
from django_enumfield import enum
import os, datetime, image_util

def user_new_unicode(self):
    return self.username if self.get_full_name() == "" else self.get_full_name()
User.__unicode__ = user_new_unicode
####################################################################################
####################################################################################
def utcnow():
    return timezone.localtime(timezone.now())

def pos(f,seq):
    i=0
    for item in seq:
        if f(item):
            return i
        i+=1

#class Common(models.Model):
#    class Meta:
#        abstract = True

class Project(models.Model):
    slug = models.SlugField(help_text="Appears in URLS")
    name = models.CharField(max_length=50)
    supervisor = models.ForeignKey(User,null=True,on_delete=models.PROTECT)
    notes = models.TextField(max_length=5000,blank=True)

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Project,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.name

class Location(models.Model):
    slug = models.SlugField(help_text="Appears in URLS")
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def save(self,*args,**kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Location,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.name

class Substrate(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def save(self,*args,**kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Substrate,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.name

class Design(models.Model):
    name = models.CharField(max_length=50)
    notes = models.TextField(max_length=5000,blank=True)
    vector_file = models.FileField(upload_to='diamond_base/design',blank=True)
    image_file = models.FileField(upload_to='diamond_base/design',blank=True)
    design_items = models.ManyToManyField('Design_Item',blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def url(self):
        return "/admin/sample_database/design/%i"%self.id

    def __unicode__(self):
        return self.name

    def get_thumbnail_url(self):
        #Returns thumbnail if exists, otherwise returns regular image
        file_path = self.image_file.path
        thumb_path = os.path.splitext(file_path)[0]+'-th.png'   #Note image_util always saves png format
        if os.path.isfile(thumb_path):
            return os.path.splitext(self.image_file.url)[0]+'-th.png'
        return self.image_file.url


class Design_Item(models.Model):
    name = models.CharField(max_length=50)
    notes= models.TextField(max_length=5000,blank=True)

    def __str__(self):
        return self.name

class Design_Object_Attachment(models.Model):
    design_object = models.ForeignKey(Design_Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    notes = models.TextField(max_length=5000,blank=True)
    file = models.FileField(upload_to='diamond_base/design/attachments',blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Sample(models.Model):
    slug = models.SlugField(help_text="Appears in URLs")
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project,null=True,blank=True,on_delete=models.PROTECT)
    location = models.ForeignKey(Location,null=True,on_delete=models.SET_NULL)
    substrate = models.ForeignKey(Substrate,null=True,on_delete=models.PROTECT)
    owner = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    last_modified_by = models.ForeignKey(User,null=True,related_name='sample_edited',on_delete=models.SET_NULL)
    last_modified = models.DateTimeField(null=True,auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(max_length=5000,blank=True)
    
    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%s (%s)'%(self.name,self.location)

    def url(self):
        return reverse('DB:sample',args=[self.id])

    def save(self,*args,**kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Sample, self).save(*args,**kwargs)

    def delete(self,*args,**kwargs):
        pieces = self.piece_set.all()
        for piece in pieces:
            piece.delete()  # Need to explicitly call this, so on a cascaded delete, it will first call the piece delete method (could also use signals)
        super(Sample,self).delete(*args,**kwargs)

class SampleMap(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    file = models.FileField(upload_to='diamond_base/SampleMap')
    date_created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(max_length=5000,blank=True)

    def get_thumbnail_url(self):
        #Returns thumbnail if exists, otherwise returns regular image
        file_path = self.file.path
        thumb_path = os.path.splitext(file_path)[0]+'-th.png'   #Note image_util always saves png format
        if os.path.isfile(thumb_path):
            return os.path.splitext(self.file.url)[0]+'-th.png'
        return self.file.url

    def save(self, *args, **kwargs):
        super(SampleMap, self).save(*args,**kwargs)   #Need to save first so file is uploaded
        #Convert TIFF formats to PNG (only for image_file)
        im_path = self.file.path
        new_path = image_util.check_and_replace_TIFF(im_path,delete=True)
        if im_path!=new_path:
            #Update the name part of the field (not full path)
            im_name = os.path.splitext(self.file.name)[0]
            self.file = im_name+'.png'
        super(SampleMap, self).save(*args,**kwargs)
        #Add a thumbnail if size is too big! Note, you could add it no matter what, but this saves space. Template just needs to agree
        image_util.thumbnail(new_path)

class Piece(models.Model):
    slug = models.SlugField(help_text="Appears in URLs")
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    design = models.ForeignKey(Design,on_delete=models.PROTECT)
    gone = models.BooleanField(default=False)
    parent = models.ForeignKey('Piece',blank=True,null=True,on_delete=models.CASCADE)   #If a piece breaks
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.__unicode__()

    def url(self):
        return reverse('DB:piece',args=[self.sample.id, self.id])
    
    def get_maps(self):
        created = self.action_set.filter(action_type__name='Created')
        if len(created)>0:
            created = created[0]
        return created.general_set.filter(data_type__name='Map File').order_by('-date')

    def get_notes(self):
        created = self.action_set.filter(action_type__name='Created')
        if len(created)>0:
            created=created[0]
        return created.notes

    def __unicode__(self):
        return u'%s (%s)'%(self.name,self.sample.name)

    def delete(self,*args,**kwargs):
        # Need to go through and clean up actions that had this as only child
        actions = self.action_set.all()
        for a in actions:
            if a.pieces.count() == 1:
                a.delete()
        super(Piece,self).delete(*args,**kwargs)

    def save(self,*args,**kwargs):
        new = False
        if not self.id:
            new = True
            self.slug = slugify(self.name)
        super(Piece, self).save(*args,**kwargs)
        if new:  # Create created action    
            create = Action(action_type=Action_Type.objects.get(name='Created'),date=utcnow())
            create.save()
            create.pieces.add(self)
            create.save()

####################################################################################
####################################################################################

class ParamType(enum.Enum):
    TEXT = 0
    INT = 1
    FLOAT = 2

    __labels__ = {
        TEXT: "Text",
        INT: "Integer",
        FLOAT: "Floating point"
    }

class Param(models.Model):
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 5000, blank = True)
    param_type = enum.EnumField(ParamType, default = ParamType.FLOAT)
    max_value = models.FloatField(null = True, blank = True)
    min_value = models.FloatField(null = True, blank = True)
    default_value = models.FloatField(null = True, blank = True)

    def __str__(self):
        return self.name

class Action_Type(models.Model):
    slug = models.SlugField(help_text="Appears in URLs")
    name = models.CharField(max_length=50,help_text="For example: Create, Experiment, Processing")
    params = models.ManyToManyField(Param, blank = True, db_table = 'sample_database_action_type_params')
    notes = models.TextField(max_length=5000, blank = True)

    def __str__(self):
        return self.__unicode__()
 
    class Meta:
        ordering = ('name',)
        verbose_name='Action Type'

    def __unicode__(self):
        fcount = self.params.all().count()
        return u'%s (%s field)'%(self.name, fcount) if fcount == 1 else u'%s (%s fields)'%(self.name, fcount)

    def url(self):
        return "/admin/sample_database/action_type/%i"%self.id
    
    def save(self,*args,**kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Action_Type, self).save(*args,**kwargs)

class Action(models.Model):
    pieces = models.ManyToManyField(Piece)
    action_type = models.ForeignKey(Action_Type, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=False)
    owner = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    last_modified_by = models.ForeignKey(User,null=True,related_name='action_edited',on_delete=models.SET_NULL)
    notes = models.TextField(max_length=5000,blank=True)
    last_modified = models.DateTimeField(auto_now_add=True)   #In Data, upon save, update this field!

#    def get(self,prop,cast=str):
#        act = self
#        field_names=act.action_type.field_names.splitlines()
#        i=pos(lambda a: prop.lower() in a.lower(),field_names)
#        if i==None:
#            raise Exception("No property named %s in %s"%(prop, act.action_type.name))
#        field_value=act.fields.splitlines()
#        return cast(field_value[i])

#    def set(self,prop,val,save=False):
#        dat=self
#        field_names=dat.action_type.field_names.splitlines()
#        i=pos(lambda a: prop.lower() in a.lower(),field_names)
#        if i==None:
#            raise Exception("No property named %s in %s"%(prop, dat.action_type.name))
#        field_value=dat.fields.splitlines()
#        field_value[i]=str(val)
#        new_fields = "\r\n".join(field_value)
#        dat.fields = new_fields
#        if save:
#             dat.save()

    def save(self,*args,**kwargs):
        self.last_modified=utcnow()
        super(Action,self).save(*args,**kwargs)
 
    def __unicode__(self):
        return u'%s'%self.action_type.name

    def __str__(self):
        return self.__unicode__()

class Param_Value_Action(models.Model):
    param = models.ForeignKey(Param, on_delete = models.CASCADE)
    action = models.ForeignKey(Action, on_delete = models.CASCADE)
    value = models.CharField(max_length = 100)


####################################################################################
####################################################################################

def get_upload_path(instance,filename):
    data_type = instance.data_type
    date = datetime.date.today().strftime('%m_%d_%Y')
    action = instance
    while type(action)!=Action:
        action = action.parent
    parent = action.pieces.all()[0]
    return os.path.join('diamond_base',data_type.name,date,parent.name,filename)

class Data_Type(models.Model):
    slug = models.SlugField(help_text="Appears in URLs")
    name = models.CharField(max_length=50,help_text="For example: SEM, Whitelight, Spectrum, Confocal, Resonant Analysis, Map")
    params = models.ManyToManyField(Param, blank = True, db_table = 'sample_database_data_type_params')
   
    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        fcount = self.params.all().count()
        return u'%s (%s field)'%(self.name, fcount) if fcount == 1 else u'%s (%s fields)'%(self.name, fcount)
    
    def save(self,*args,**kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Data_Type, self).save(*args,**kwargs)

    class Meta:
        verbose_name='Data Type'

class Data(models.Model):
    data_type = models.ForeignKey(Data_Type,on_delete=models.CASCADE)
    image_file = models.FileField(upload_to=get_upload_path,blank=True) #image file
    raw_data = models.FileField(upload_to=get_upload_path,blank=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(max_length=5000,blank=True)

#    def get(self,prop,cast=str):
#        dat = self
#        field_names=dat.data_type.field_names.splitlines()
#        i=pos(lambda a: prop.lower() in a.lower(),field_names)
#        if i==None:
#            raise Exception("No property named %s in %s"%(prop, dat.data_type.name))
#        field_value=dat.fields.splitlines()
#        return cast(field_value[i])
#
#    def set(self,prop,val,save=False):
#        dat=self
#        field_names=dat.data_type.field_names.splitlines()
#        i=pos(lambda a: prop.lower() in a.lower(),field_names)
#        if i==None:
#            raise Exception("No property named %s in %s"%(prop, dat.data_type.name))
#        field_value=dat.fields.splitlines()
#        field_value[i]=str(val)
#        new_fields = "\r\n".join(field_value)
#        dat.fields = new_fields
#        if save:
#            dat.save()

    def get_thumbnail_url(self):
        #Returns thumbnail if exists, otherwise returns regular image
        if self.image_file=='':
            return ''
        file_path = self.image_file.path
        thumb_path = os.path.splitext(file_path)[0]+'-th.png'   #Note image_util always saves png format
        if os.path.isfile(thumb_path):
            return os.path.splitext(self.image_file.url)[0]+'-th.png'
        return self.image_file.url

    def save(self, *args, **kwargs):
        super(Data, self).save(*args,**kwargs)   #Need to save first so file is uploaded

        if self.image_file.name != None and self.image_file.name != '':
            #Convert TIFF formats to PNG (only for image_file)
            im_path = ''
            try:
                im_path = self.image_file.path
                new_path = image_util.check_and_replace_TIFF(im_path,delete=True)
            except (IOError,ValueError):
                new_path = im_path
            if im_path!=new_path:
                #Update the name part of the field (not full path)
                im_name = os.path.splitext(self.image_file.name)[0]
                self.image_file = im_name+'.png'
            super(Data, self).save(*args,**kwargs)
            #Add a thumbnail if size is too big! Note, you could add it no matter what, but this saves space. Template just needs to agree
            try:  #Permission denied if SSH...
                image_util.thumbnail(new_path)
            except IOError:
                pass

        action = self
        while type(action)!=Action:
            action=action.parent
        action.last_modified=utcnow()
        action.save()

    def __unicode__(self):
        return self.data_type.name

    def __str__(self):
        return self.data_type.name

class Param_Value_Data(models.Model):
    param = models.ForeignKey(Param, on_delete = models.CASCADE)
    data = models.ForeignKey(Data, on_delete = models.CASCADE)
    value = models.CharField(max_length = 100)


####################################################################################

class General(Data):
#Note 2 foreign keys (1 from Data)
    parent = models.ForeignKey(Action, on_delete=models.CASCADE)
    xmin = models.FloatField(blank=True)
    xmax = models.FloatField(blank=True)
    ymin = models.FloatField(blank=True)
    ymax = models.FloatField(blank=True)

    class Meta:
        verbose_name='General Data'
        verbose_name_plural=verbose_name

class Local(Data):
#Note 2 foreign keys (1 from Data)
    parent = models.ForeignKey(General, on_delete=models.CASCADE)
    x = models.FloatField()
    y = models.FloatField()

    class Meta:
        verbose_name='Local Data'
        verbose_name_plural=verbose_name

class Local_Attachment(Data):
#Note 2 foreign keys (1 from Data)
    parent = models.ForeignKey(Local, on_delete=models.CASCADE)



