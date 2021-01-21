# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-03 04:58
from __future__ import unicode_literals

from django.db import migrations


INITIAL_QUESTIONS = [
    'Hosting services to support research',
    'Collaboration platform',
    'Hosting a website',
    'Hosting a database',
    'Hosting and sharing data',
    'Collaborating with other institutions',
    'Collaborating internationally',
    'Machine learning',
    'Data analysis',
    'Modelling and simulation',
    'Other',
]


class Migration(migrations.Migration):

    def addUsageTypes(apps, schema_editor):
        UsageType = apps.get_model('rcallocation', 'UsageType')
        for name in INITIAL_QUESTIONS:
            UsageType.objects.create(name=name, enabled=True)

    def removeUsageTypes(apps, schema_editor):
        UsageType = apps.get_model('rcallocation', 'UsageType')
        UsageType.objects.all().delete();

    dependencies = [
        ('rcallocation', '0051_add_usage_surveys'),
    ]

    operations = [
        migrations.RunPython(addUsageTypes, removeUsageTypes)
    ]
