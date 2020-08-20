# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-08-20 23:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0035_add-zone-enabled-field'),
    ]

    operations = [
        migrations.CreateModel(
            name='Approver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.EmailField(max_length=254, unique=True)),
                ('display_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('display_name', models.CharField(max_length=64)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='approver',
            name='sites',
            field=models.ManyToManyField(to='rcallocation.Site'),
        ),
    ]