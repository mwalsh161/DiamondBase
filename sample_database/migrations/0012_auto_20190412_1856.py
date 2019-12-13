# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sample_database', '0011_auto_20190412_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='sample_database.Location', null=True),
        ),
    ]
