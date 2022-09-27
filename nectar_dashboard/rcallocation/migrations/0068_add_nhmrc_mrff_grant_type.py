# Generated by Django 2.2.12 on 2022-09-27 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0067_auto_20220811_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grant',
            name='grant_subtype',
            field=models.CharField(choices=[(None, 'Select a grant subtype'), ('arc-discovery', 'ARC Discovery project'), ('arc-indigenous', 'ARC Discovery Indigenous'), ('arc-decra', 'ARC Discovery Early Career Researcher Award'), ('arc-future', 'ARC Future Fellowship'), ('arc-laureate', 'ARC Laureate Fellowship'), ('arc-itrp', 'ARC Industry Transformation Research Program'), ('arc-linkage', 'ARC Linkage Project'), ('arc-coe', 'ARC Centre of Excellence'), ('arc-lief', 'ARC Linkage Infrastructure Equipment and Facilities'), ('arc-sri', 'ARC Special Research Initiative'), ('arc-llasp', 'ARC Linkage Learned Academies Special Project'), ('arc-other', 'Other ARC grant'), ('nhmrc-investigator', 'NHMRC Investigator grant'), ('nhmrc-synergy', 'NHMRC Synergy grant'), ('nhmrc-ideas', 'NHMRC Ideas grant'), ('nhmrc-strategic', 'NHMRC Strategic or Leverage grant'), ('nhmrc-program', 'NHMRC Program grant'), ('nhmrc-project', 'NHMRC Project grant'), ('nhmrc-fas', 'NHMRC Fellowship or Scholarship (various)'), ('nhmrc-core', 'NHMRC Center of Research Excellence'), ('nhmrc-development', 'NHMRC Development grant'), ('nhmrc-equipment', 'NHMRC Equipment grant'), ('nhmrc-ctcs', 'NHMRC Clinical Trial and Cohort Studies grant'), ('nhmrc-ics', 'NHMRC International Collaborations (various)'), ('nhmrc-mrff', 'NHMRC Medical Research Future Fund'), ('nhmrc-pc', 'NHMRC Partnership Centre'), ('nhmrc-pp', 'NHMRC Partnership project'), ('nhmrc-tcr', 'NHMRC Targeted Calls for Research'), ('nhmrc-iriiss', 'NHMRC Independent Research Institute Infrastructure Support Scheme'), ('nhmrc-bdri', 'NHMRC Boosting Dementia Research Initiatives (various)'), ('nhmrc-other', 'Other NHMRC scheme'), ('rdc-wa', 'Wine Australia'), ('rdc-crdc', 'Cotton RDC'), ('rdc-frdc', 'Fisheries RDC'), ('rdc-grdc', 'Grains RDC'), ('rdc-agrifutures', 'Rural Industries RDC (AgriFutures Australia)'), ('rdc-ael', 'Australian Eggs Ltd'), ('rdc-livecorp', 'Australian Livestock Export Corp Ltd (LiveCorp)'), ('rdc-ampc', 'Australian Meat Processor Corp'), ('rdc-apl', 'Australian Pork Ltd'), ('rdc-awil', 'Australian Wool Innovation Ltd'), ('rdc-dal', 'Dairy Australia Ltd'), ('rdc-fwpa', 'Forest and Wood Products Australia'), ('rdc-hial', 'Horticulture Innovation Australia Ltd'), ('rdc-mla', 'Meat and Livestock Australia'), ('rdc-sral', 'Sugar Research Australia Ltd'), ('act', 'Australian Capital Territory Govt funding'), ('nsw', 'New South Wales Govt funding'), ('nt', 'Northern Territory Govt funding'), ('qld', 'Queensland Govt funding'), ('sa', 'South Australia Govt funding'), ('tas', 'Tasmania Govt funding'), ('vic', 'Victoria Govt funding'), ('wa', 'Western Australia Govt funding'), ('unspecified', 'unspecified')], help_text="Choose an applicable grant subtype from the\n                  dropdown options.  If no option is applicable,\n                  choose 'unspecified' and then fill in the 'Other\n                  funding source details' field below.", max_length=128, verbose_name='Grant Subtype'),
        ),
    ]
