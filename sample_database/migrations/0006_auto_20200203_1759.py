# Generated by Django 3.0.2 on 2020-02-03 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sample_database', '0005_auto_20200203_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='params',
            field=models.ManyToManyField(to='sample_database.Param'),
        ),
        migrations.AddField(
            model_name='data',
            name='params',
            field=models.ManyToManyField(to='sample_database.Param'),
        ),
    ]