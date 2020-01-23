# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample_database', '0012_auto_20190412_1856'),
    ]

    operations = [
        migrations.CreateModel(
            name='acidclean',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('temperature', models.FloatField(help_text=b'Celsius')),
                ('start_time', models.DateTimeField()),
                ('stop_time', models.DateTimeField(null=True)),
                ('issued_start_user', models.CharField(max_length=50)),
                ('issued_stop_user', models.CharField(max_length=50)),
                ('issued_start_time', models.DateTimeField()),
                ('issued_stop_time', models.DateTimeField()),
                ('diamonds', models.ManyToManyField(to='sample_database.Sample')),
            ],
        ),
    ]
