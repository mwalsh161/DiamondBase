from django.db import models
#from django.core import urlresolvers
from django.utils import timezone
import os, datetime

class Computer(models.Model):
    name = models.CharField(max_length=100)
    ip = models.CharField(max_length=15)
    notes = models.TextField(max_length=5000,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField()

    def __unicode__(self):
        return u'%s: %s'%(self.name,self.ip)

    def __str__(self):
        return self.__unicode__()

    def save(self,*args,**kwargs):
        self.date_modified=timezone.now()
        super(Computer,self).save(*args,**kwargs)
