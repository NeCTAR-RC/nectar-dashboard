# Generated by Django 3.2.18 on 2024-07-26 03:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0078_add_impact_statement'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocationrequest',
            name='active_service_count',
            field=models.IntegerField(
                error_messages={
                    'min_value': 'The number cannot be less than 0'
                },
                help_text='Estimate the number of research services or research\n                 platforms (also called virtual research environments of\n                 virtual laboratories) that were hosted on your allocation\n                 resources at any time during the last year. These could be\n                 web sites, web applications, databases or data repositories.\n                 Do not include application software that is run by users who\n                 log in to the virtual machine instance and run the\n                 application themselves, e.g. from the command line.',
                null=True,
                validators=[django.core.validators.MinValueValidator(-1)],
                verbose_name='Number of active research services or platforms hosted using this allocation',
            ),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='direct_access_user_estimate',
            field=models.IntegerField(
                error_messages={
                    'min_value': 'The estimated number of users must be greater than 0'
                },
                help_text='Estimated number of users who will be creating virtual\n                machine instances or directly logging in to them.',
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Estimated number of users who will directly access the instances',
            ),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='direct_access_user_past_year',
            field=models.IntegerField(
                error_messages={
                    'min_value': 'The number of users must be greater than 0'
                },
                help_text='Number of users who have created virtual machine\n                 instances or directly logged in to them in the last year.',
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Number of users directly accessing instances over the past year',
            ),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='estimated_service_active_users',
            field=models.IntegerField(
                error_messages={
                    'min_value': 'The estimated number of users must be greater than 0'
                },
                help_text='Estimate the number of people you expect will use the\n                 research services or platforms hosted on your allocation.\n                 Note that when you renew your Nectar allocation we will ask\n                 you to estimate the number of unique active users of these\n                 services over the previous year.',
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Estimated total number of unique active users of these services',
            ),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='estimated_service_count',
            field=models.IntegerField(
                error_messages={
                    'min_value': 'The estimated number cannot be less than 0'
                },
                help_text='Estimate the number of research services or research\n                 platforms (also called virtual research environments or\n                 virtual laboratories) you expect to be hosted on your\n                 allocation. These could be web sites, web applications,\n                 databases or data repositories. Do not include application\n                 software that is run by users who log in to the virtual\n                 machine instance and run the application themselves,\n                 e.g. from the command line.',
                null=True,
                validators=[django.core.validators.MinValueValidator(-1)],
                verbose_name='Estimated number of research services or platforms to be hosted using this allocation',
            ),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='multiple_allocations_check',
            field=models.BooleanField(
                default=False,
                verbose_name='Does the research project have more than one allocation\n         on the Nectar Cloud where the number of users has already been\n         provided in a separate allocation?',
            ),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='service_active_users_past_year',
            field=models.IntegerField(
                error_messages={
                    'min_value': 'The number of users must be greater than 0'
                },
                help_text='The number of individuals who have used the research\n                 services or platforms hosted on your allocation in the last\n                 year (or less if they have been operating for less than a\n                 year). Specify if this number is measured (e.g. you can\n                 accurately measure the number of individuals who have logged\n                 in to your service in the last year) or estimated (please\n                 provide conservative, justifiable estimates).',
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Total number of unique active users of these services over the past year',
            ),
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='users_figure_type',
            field=models.CharField(
                choices=[('measured', 'Measured'), ('estimated', 'Estimated')],
                default='measured',
                max_length=10,
                verbose_name='Are the above figures measured or estimated?',
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='estimated_number_users',
            field=models.IntegerField(
                editable=False,
                error_messages={
                    'min_value': 'The estimated number of users must be greater than 0'
                },
                help_text='Estimated number of users, researchers and collaborators\n        to be supported by the allocation.',
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Estimated number of users',
            ),
        ),
    ]