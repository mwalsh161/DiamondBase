# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sample_database', '0009_auto_20190410_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='last_modified_by',
            field=models.ForeignKey(related_name='action_edited', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
