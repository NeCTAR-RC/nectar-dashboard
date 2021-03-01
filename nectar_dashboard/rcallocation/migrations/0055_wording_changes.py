# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-07 00:30
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0054_add_publication_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='doi',
            field=models.CharField(blank=True, default='', help_text="Provide the Research Output's DOI.  A DOI should be\n               provided for all books and peer-reviewed papers.  A valid\n               DOI starts with '10.&lt;number&gt;/'.  This is followed by\n               letters, numbers and other characters.  For example:\n               '10.23456/abc-123'.", max_length=256, validators=[django.core.validators.RegexValidator(message="Invalid DOI.  A DOI looks like\n                                      '10.<digits>/<characters>' with\n                                      the restriction that there are no\n                                      whitespace or control chars in\n                                      <characters>", regex=re.compile('^10.\\d{4,9}/[^\x00-\x1f\x7f-\x9f\\s]+$', 32))], verbose_name='Digital Object Identifier (DOI)'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='output_type',
            field=models.CharField(choices=[(None, 'Select an output type'), ('AJ', 'Peer reviewed journal article'), ('AP', 'Other peer reviewed paper'), ('AN', 'Non-peer reviewed paper'), ('B', 'Book or book chapter'), ('M', 'Media publication'), ('D', 'Dataset'), ('S', 'Software'), ('P', 'Patent'), ('O', 'Other'), ('U', 'Unspecified')], default='U', help_text="Select a publication type that best describes\n                the publication.  The 'Media publication' type is\n                intended to encompass traditional media and 'new'\n                media such as websites, blogs and social media.", max_length=2, verbose_name='Research Output type'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication',
            field=models.CharField(blank=True, help_text="Provide details of the Research Output according to its\n                type.  For example a Paper or Book's citation, a Dataset's\n                title and URI, Software product's name and website URL,\n                a Patent's title and number.  This field should not be\n                used for Research Outputs with DOIs known to CrossRef.", max_length=512, verbose_name='Details of Research Output'),
        ),
    ]
