# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sample_database', '0010_auto_20190412_1701'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action_type',
            options={'ordering': ('name',), 'verbose_name': 'Action Type'},
        ),
        migrations.AlterModelOptions(
            name='design',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='substrate',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='action',
            name='last_modified_by',
            field=models.ForeignKey(related_name='action_edited', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='action',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='data',
            name='data_type',
            field=models.ForeignKey(to='sample_database.Data_Type', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='piece',
            name='design',
            field=models.ForeignKey(to='sample_database.Design', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='piece',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='sample_database.Piece', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='last_modified_by',
            field=models.ForeignKey(related_name='sample_edited', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sample_database.Location', null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='sample_database.Project', null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='substrate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sample_database.Substrate', null=True),
        ),
    ]
