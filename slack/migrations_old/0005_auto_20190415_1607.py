# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slack', '0004_auto_20190415_1343'),
    ]

    operations = [
        migrations.CreateModel(
            name='failed_regex_strings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.CharField(max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.CharField(max_length=50)),
                ('error', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='acidclean',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
