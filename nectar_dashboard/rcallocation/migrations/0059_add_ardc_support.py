# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-24 04:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0058_populate_ncris_facilities'),
    ]

    operations = [
        migrations.CreateModel(
            name='ARDCSupport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Full ARDC program or project name')),
                ('short_name', models.CharField(max_length=200, unique=True, verbose_name='Common short name or acronym')),
                ('project', models.BooleanField(default=True, help_text='True for projects, false for programs', verbose_name='Distinguishes projects from programs')),
                ('project_id', models.CharField(blank=True, max_length=20, verbose_name='ARDC project ID')),
                ('hide', models.BooleanField(default=False, help_text='True hides the program or project', verbose_name='Determines if the user can choose this program or project')),
                ('explain', models.BooleanField(default=False, help_text='When true, the ARDC Support Details field should provide details.  This is typically used for programs rather than projects', verbose_name='Determines if this program or project requires more details')),
            ],
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='ardc_explanation',
            field=models.CharField(blank=True, help_text='Provide details of how the ARDC program(s)\n        supported this request.', max_length=1024, verbose_name='ARDC Support details'),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='ardc_support',
            field=models.ManyToManyField(blank=True, to='rcallocation.ARDCSupport'),
        ),
    ]
