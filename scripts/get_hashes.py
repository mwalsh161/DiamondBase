import sys, os, datetime
sys.path.append('/home/diamondbase/DiamondBase')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")
import django
django.setup()
from django.db import models
from django.contrib.auth.models import User


if __name__ == '__main__':
    users = User.objects.all()
    for u in users:
        out = '%s:%s:'%(u.username,u.password)
        print out
