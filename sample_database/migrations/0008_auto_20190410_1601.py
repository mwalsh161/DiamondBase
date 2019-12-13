# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sample_database', '0007_action_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'Appears in URLS')),
                ('name', models.CharField(max_length=50)),
                ('notes', models.TextField(max_length=5000, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='sample',
            name='last_modified_by',
            field=models.ForeignKey(related_name='sample_edited', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='project',
            field=models.ForeignKey(to='sample_database.Project', null=True),
        ),
    ]
