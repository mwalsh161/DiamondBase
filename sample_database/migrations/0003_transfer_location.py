# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def link_location(apps, schema_editor):
    Sample = apps.get_model('sample_database','Sample')
    Location = apps.get_model('sample_database','Location')
    for sample in Sample.objects.all():
        location = Location.objects.get(name=sample.location)
        sample.location_link = location
        sample.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sample_database', '0002_sample_location_link'),
    ]

    operations = [
        migrations.RunPython(link_location),
    ]
