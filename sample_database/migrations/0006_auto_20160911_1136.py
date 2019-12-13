# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sample_database', '0005_auto_20160726_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='Substrate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='sample',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='substrate',
            field=models.ForeignKey(to='sample_database.Substrate', null=True),
        ),
    ]
