# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-25 07:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0052_populate_survey_questions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='usage_patterns',
            field=models.TextField(blank=True, help_text='Explain why you need Nectar Research Cloud resources, and how they will be used to support your research. Include relevant technical information on your proposed use of the resources; e.g. software applications, characteristics of computational tasks, data quantities and access patterns, frequency and intensity of utilization, and so on.  We will use this information to help us decide if the resources that you are requesting are appropriate to the tasks to be performed.', max_length=1024, verbose_name='Justification and details of your Proposed Cloud Usage'),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='use_case',
            field=models.TextField(help_text='This section should provide a brief overview of the Research Project or Projects that the requested allocation would directly support. We will use this information to help prioritize the allocation of resources to different projects.', max_length=4096, verbose_name='Research project description'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='grant_subtype',
            field=models.CharField(choices=[(None, 'Select a grant subtype'), ('arc-discovery', 'ARC Discovery project'), ('arc-indigenous', 'ARC Discovery Indigenous'), ('arc-decra', 'ARC Discovery Early Career Researcher Award'), ('arc-future', 'ARC Future Fellowship'), ('arc-laureate', 'ARC Laureate Fellowship'), ('arc-itrp', 'ARC Industry Transformation Research Program'), ('arc-linkage', 'ARC Linkage Project'), ('arc-coe', 'ARC Centre of Excellence'), ('arc-lief', 'ARC Linkage Infrastructure Equipment and Facilities'), ('arc-sri', 'ARC Special Research Initiative'), ('arc-llasp', 'ARC Linkage Learned Academies Special Project'), ('arc-other', 'Other ARC grant'), ('nhmrc-investigator', 'NHMRC Investigator grant'), ('nhmrc-synergy', 'NHMRC Synergy grant'), ('nhmrc-ideas', 'NHMRC Ideas grant'), ('nhmrc-strategic', 'NHMRC Strategic or Leverage grant'), ('nhmrc-program', 'NHMRC Program grant'), ('nhmrc-project', 'NHMRC Project grant'), ('nhmrc-fas', 'NHMRC Fellowship or Scholarship (various)'), ('nhmrc-core', 'NHMRC Center of Research Excellence'), ('nhmrc-development', 'NHMRC Development grant'), ('nhmrc-equipment', 'NHMRC Equipment grant'), ('nhmrc-ctcs', 'NHMRC Clinical Trial and Cohort Studies grant'), ('nhmrc-ics', 'NHMRC International Collaborations (various)'), ('nhmrc-pc', 'NHMRC Partnership Centre'), ('nhmrc-pp', 'NHMRC Partnership project'), ('nhmrc-tcr', 'NHMRC Targeted Calls for Research'), ('nhmrc-iriiss', 'NHMRC Independent Research Institute Infrastructure Support Scheme'), ('nhmrc-bdri', 'NHMRC Boosting Dementia Research Initiatives (various)'), ('nhmrc-other', 'Other NHMRC scheme'), ('act', 'Australian Capital Territory Govt funding'), ('nsw', 'New South Wales Govt funding'), ('nt', 'Northern Territory Govt funding'), ('qld', 'Queensland Govt funding'), ('sa', 'South Australia Govt funding'), ('tas', 'Tasmania Govt funding'), ('vic', 'Victoria Govt funding'), ('wa', 'Western Australia Govt funding'), ('unspecified', 'unspecified')], help_text="Choose an applicable grant subtype from the\n                  dropdown options.  If no option is applicable,\n                  choose 'unspecified' and then fill in the 'Other\n                  funding source details' field below.", max_length=128, verbose_name='Grant Subtype'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='grant_type',
            field=models.CharField(choices=[(None, 'Select a grant type'), ('arc', 'Australian Research Council'), ('nhmrc', 'NHMRC'), ('comp', 'Other Australian Federal Govt competitive grant'), ('govt', 'Australian Federal Govt non-competitive funding'), ('state', 'Australian State / Territory Govt funding'), ('industry', 'Industry funding'), ('ext', 'Other external funding'), ('inst', 'Institutional research funding'), ('nz', 'New Zealand research funding')], help_text='Choose the grant type from the dropdown options.', max_length=128, verbose_name='Grant Type'),
        ),
    ]
