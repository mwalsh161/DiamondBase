# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample_database', '0004_remove_sample_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sample',
            old_name='location_link',
            new_name='location',
        ),
    ]
