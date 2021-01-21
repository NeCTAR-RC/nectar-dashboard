# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-01-21 05:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0050_backfill_arc_grant_subtypes'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsageSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usage_type', models.CharField(max_length=128, verbose_name='Usage Type')),
                ('usage', models.BooleanField(verbose_name='Usage')),
            ],
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='usage_survey_version',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='usagesurvey',
            name='allocation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to='rcallocation.AllocationRequest'),
        ),
        migrations.AlterUniqueTogether(
            name='usagesurvey',
            unique_together=set([('allocation', 'usage_type')]),
        ),
    ]
