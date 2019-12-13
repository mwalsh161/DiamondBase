# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slack', '0003_auto_20190415_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acidclean',
            name='issued_stop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='acidclean',
            name='issued_stop_user',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='acidclean',
            name='stop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
