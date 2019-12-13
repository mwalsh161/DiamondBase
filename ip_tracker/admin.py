from ip_tracker.models import *
from django.contrib import admin

class ComputerAdmin(admin.ModelAdmin):
    list_display=('name','ip','notes')

admin.site.register(Computer,ComputerAdmin)
