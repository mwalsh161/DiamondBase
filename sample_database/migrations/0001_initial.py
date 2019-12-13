# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sample_database.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fields', models.TextField(max_length=500, blank=True)),
                ('date', models.DateTimeField()),
                ('notes', models.TextField(max_length=5000, blank=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Action_Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'Appears in URLs')),
                ('name', models.CharField(help_text=b'For example: Create, Experiment, Processing', max_length=50)),
                ('field_names', models.TextField(help_text=b'Fields that will be in all of this type (other than date/notes).  Spearate items by a newline.  Limited to 500 characters.', max_length=500, verbose_name=b'Field names', blank=True)),
            ],
            options={
                'verbose_name': 'Action Type',
            },
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fields', models.TextField(max_length=500, blank=True)),
                ('image_file', models.FileField(upload_to=sample_database.models.get_upload_path, blank=True)),
                ('raw_data', models.FileField(upload_to=sample_database.models.get_upload_path, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(max_length=5000, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Data_Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'Appears in URLs')),
                ('name', models.CharField(help_text=b'For example: SEM, Whitelight, Spectrum, Confocal, Resonant Analysis, Map', max_length=50)),
                ('field_names', models.TextField(help_text=b'Fields that will be in all of this type (other than date/notes).  Spearate items by a newline.  Limited to 500 characters.', max_length=500, verbose_name=b'Field names', blank=True)),
            ],
            options={
                'verbose_name': 'Data Type',
            },
        ),
        migrations.CreateModel(
            name='Design',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('notes', models.TextField(max_length=5000, blank=True)),
                ('vector_file', models.FileField(upload_to=b'diamond_base/design', blank=True)),
                ('image_file', models.FileField(upload_to=b'diamond_base/design', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Design_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('notes', models.TextField(max_length=5000, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Design_Object_Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField(max_length=5000, blank=True)),
                ('file', models.FileField(upload_to=b'diamond_base/design/attachments', blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('design_object', models.ForeignKey(to='sample_database.Design_Item')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'Appears in URLS')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'Appears in URLs')),
                ('name', models.CharField(max_length=50)),
                ('gone', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('design', models.ForeignKey(to='sample_database.Design')),
                ('parent', models.ForeignKey(blank=True, to='sample_database.Piece', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'Appears in URLs')),
                ('name', models.CharField(max_length=50)),
                ('location', models.CharField(default=b'MIT', max_length=50, choices=[(b'MIT', b'MIT'), (b'BNL', b'BNL'), (b'Columbia', b'Columbia')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(max_length=5000, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SampleMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'diamond_base/SampleMap')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(max_length=5000, blank=True)),
                ('sample', models.ForeignKey(to='sample_database.Sample')),
            ],
        ),
        migrations.CreateModel(
            name='General',
            fields=[
                ('data_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sample_database.Data')),
                ('xmin', models.FloatField(blank=True)),
                ('xmax', models.FloatField(blank=True)),
                ('ymin', models.FloatField(blank=True)),
                ('ymax', models.FloatField(blank=True)),
            ],
            options={
                'verbose_name': 'General Data',
                'verbose_name_plural': 'General Data',
            },
            bases=('sample_database.data',),
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('data_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sample_database.Data')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('parent', models.ForeignKey(to='sample_database.General')),
            ],
            options={
                'verbose_name': 'Local Data',
                'verbose_name_plural': 'Local Data',
            },
            bases=('sample_database.data',),
        ),
        migrations.CreateModel(
            name='Local_Attachment',
            fields=[
                ('data_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sample_database.Data')),
                ('parent', models.ForeignKey(to='sample_database.Local')),
            ],
            bases=('sample_database.data',),
        ),
        migrations.AddField(
            model_name='piece',
            name='sample',
            field=models.ForeignKey(to='sample_database.Sample'),
        ),
        migrations.AddField(
            model_name='design',
            name='design_items',
            field=models.ManyToManyField(to='sample_database.Design_Item', blank=True),
        ),
        migrations.AddField(
            model_name='data',
            name='data_type',
            field=models.ForeignKey(to='sample_database.Data_Type'),
        ),
        migrations.AddField(
            model_name='action',
            name='action_type',
            field=models.ForeignKey(to='sample_database.Action_Type'),
        ),
        migrations.AddField(
            model_name='action',
            name='pieces',
            field=models.ManyToManyField(to='sample_database.Piece'),
        ),
        migrations.AddField(
            model_name='general',
            name='parent',
            field=models.ForeignKey(to='sample_database.Action'),
        ),
    ]
