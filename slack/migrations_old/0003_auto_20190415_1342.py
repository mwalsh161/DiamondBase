# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slack', '0002_auto_20190415_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acidclean',
            name='diamonds',
            field=models.ManyToManyField(related_name='+', to='sample_database.Sample', blank=True),
        ),
    ]
