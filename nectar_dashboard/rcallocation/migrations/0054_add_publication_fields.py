# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-01 05:20
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0053_wording_changes'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='doi_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='publication',
            name='output_type',
            field=models.CharField(choices=[('AJ', 'Peer reviewed journal article'), ('AP', 'Other peer reviewed paper'), ('AN', 'Non-peer reviewed paper'), ('B', 'Book or book chapter'), ('M', 'Media publication'), ('D', 'Dataset'), ('S', 'Software'), ('P', 'Patent'), ('O', 'Other'), ('U', 'Unspecified')], default='U', help_text="Select a publication type that best describes\n                the publication.  The 'Media publication' type is \n                intended to encompass traditional media and 'new'\n                media such as websites, blogs and social media.", max_length=2, verbose_name='Research Output type'),
        ),
        migrations.AddField(
            model_name='publication',
            name='title',
            field=models.CharField(blank=True, max_length=256, verbose_name='Title of publication'),
        ),
        migrations.AddField(
            model_name='publication',
            name='year',
            field=models.IntegerField(null=True, verbose_name='Year published'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='doi',
            field=models.CharField(blank=True, default='', help_text="Provide the research output's DOI.  For example:\n               '10.23456/more-stuff'.  A DOI is mandatory for peer-reviewed\n               publications.", max_length=256, validators=[django.core.validators.RegexValidator(message="Invalid DOI.  A DOI looks like\n                                      '10.<digits>/<characters>' with\n                                      the restriction that there are no\n                                      whitespace or control chars in\n                                      <characters>", regex=re.compile('^10.\\d{4,9}/[^\x00-\x1f\x7f-\x9f\\s]+$', 32))], verbose_name='Digital Object Identifier (DOI)'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication',
            field=models.CharField(blank=True, help_text='A full citation style text reference\n                for this research output; e.g. include article/title,\n                authors, journal/outlet and year.', max_length=512, verbose_name='Citation reference'),
        ),
    ]
