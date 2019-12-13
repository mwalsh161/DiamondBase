'''This code will save a binary file that stores the database in some format that it aslo reads.
   It will restore that data to a brand new database as long as required fields weren't added, or field names weren't changed.
   If required fields were added/changed, you can edit the load() function below to make a mapping.

mpwalsh@mit.edu
6/30/2014
'''

import sys, os, datetime
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
from django.db import models as django_models
from sample_database import models as my_models
import json

fname = 'DBdump.dat'
DELIM = '@@'
DELIM_MOD = '@&'
DONT_INCLUDE= ['Data','Design_Object','DesignAttach']
ORDER = ['Design','Sample','SampleMap','Piece','Action_Type','Action','Data_Type','General','Local','Local_Attachment']

def get_models():
	test_type=type(my_models.Action)   #Need any existing models to find the rest
	models={}
	for property,value in vars(my_models).iteritems():
		if type(value)==test_type:
			models[property]=value
	return models

def get_fields(model,model_names):
	fields={}
	for f in model._meta.fields+model._meta.many_to_many:
                val = getattr(model,f.name)
		dat_type = type(val).__name__
		if dat_type in model_names:
			fields[f.name]=[str(val.id),dat_type]
		elif dat_type=='ManyRelatedManager':
			fields[f.name]=[str([obj.id for obj in val.all()]),dat_type]
		elif dat_type=='FieldFile':
			try:
				fields[f.name]=[val.path,dat_type]
			except ValueError:
				fields[f.name]=['','NoneType']
		elif dat_type=='datetime':
			fields[f.name]=[str(list(val.timetuple()[0:7])),dat_type]
		else:
			fields[f.name]=[str(val),dat_type]
	return fields

def backup():
	models=get_models()
	print 'Opening '+fname
	with open(fname,'wb') as f:
		for name in ORDER:
			if name not in DONT_INCLUDE:	#Redundant to the superclasses
				entries=models[name].objects.all().order_by('id')
				print 'Going through '+name+' Objects ('+str(len(entries))+')'
				f.write(DELIM_MOD)
				for entry in entries:
					fields=get_fields(entry,models.keys())
					f.write(json.dumps(fields)+DELIM)	#Encodes basic objects to string (lists/dicts)

def load():
	models=get_models()
	print 'Opening '+fname
	with open(fname,'rb') as f:
		data = f.read()
	models_DAT = data.split(DELIM_MOD)[1:]	#Because the DELIM_MOD is appended to beginnig as well
	i=0	#To keep track of where we are in ORDER
	for model_DAT in models_DAT:
		print 'Unpacking '+ORDER[i]
		entries = model_DAT.split(DELIM)
		entries = entries[0:len(entries)-1]
		for entry in entries:
			fields=json.loads(entry)	#Decodes string to basic objects (lists/dicts)
			model=models[ORDER[i]]()	#Note, this is calling the constructor of the current model
			M2M={}				#Keep track of many_to_many
			for field in fields.keys():	#id set automatically upon save
				if '_ptr' not in field:	#Django uses a oneToOneField between parent model vi`:wa _ptr
					skip=False
					val,Type=fields[field]
					if Type!='NoneType':
						if Type in models.keys():
							try:
								val=eval("my_models.%s.objects.get(id=%i)"%(Type,int(val)))
							except Exception as err:
								print Type,val,fields
								raise err
						elif Type=='ManyRelatedManager':
							M2M[field]=json.loads(val)
							skip=True
						elif Type=='datetime':
							val=datetime.datetime(*json.loads(val))
						elif Type=='FieldFile':
							val=val[17:]	#Remove /Volumes/Houston/
						else:
							try:
								val=eval("%s('''%s''')"%(Type,val))	#Cast to original type
							except Exception as err:
								print fields
								raise err
						if not skip:
							setattr(model,field,val)
			try:
				model.save()
			except Exception as err:
				print fields
				raise err
			for el in M2M.keys():
				related_model=el[0:len(el)-1].capitalize()	#Hopefully you did it this way...
				related_model_objs=[eval("my_models.%s.objects.get(id=%i)"%(related_model,obj)) for obj in M2M[el]]
				for obj in related_model_objs:
					eval("model.%ss.add(obj)"%related_model.lower())
		i+=1

if __name__ == "__main__":
	if len(sys.argv)==2:
		if sys.argv[1]=='backup':
			backup()
			print 'Done'
		elif sys.argv[1]=='load':
			load()
			print 'Done'
		else:
			print "Either 'backup' or 'load'.  Loading is permanent!"
	else:
		print "Either 'backup' or 'load'.  Loading is permanent!"
