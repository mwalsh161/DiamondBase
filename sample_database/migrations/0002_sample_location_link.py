# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample_database', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='location_link',
            field=models.ForeignKey(to='sample_database.Location', null=True),
        ),
    ]
