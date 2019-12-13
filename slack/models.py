from django.db import models
from django.contrib.auth.models import User
from sample_database.models import Sample, Action_Type, Action

class acidclean(models.Model):
    diamonds = models.ManyToManyField(Sample,related_name='+',blank=True)
    temperature = models.FloatField(help_text='Celsius')
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField(null=True,blank=True) # Adding this signals complete
    processed = models.BooleanField(default=False)

    # Info pertainint go slack request
    ## (can't assume name in slack matches diamondbase,
    ##  so save Char instead of ForeignKey)
    issued_start_user = models.CharField(max_length=50)
    issued_stop_user = models.CharField(max_length=50,null=True,blank=True)
    issued_start_time = models.DateTimeField()
    issued_stop_time = models.DateTimeField(null=True,blank=True)
    
class failed_regex_strings(models.Model):
    string = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=50)
    error = models.TextField()

    def __unicode__(self):
        return self.string