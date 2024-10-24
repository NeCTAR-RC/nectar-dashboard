# Generated by Django 3.2.18 on 2024-08-08 04:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0079_auto_20240726_0316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='multiple_allocations_check',
            field=models.BooleanField(
                default=False,
                null=True,
                verbose_name='Does the research project have more than one allocation\n         on the Nectar Cloud where the number of users has already been\n         provided in a separate allocation?',
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='nectar_benefit_description',
            field=models.TextField(
                blank=True,
                help_text='Briefly describe how the use of Nectar has benefited your research activity.',
                max_length=4096,
                null=True,
                verbose_name='Benefits of Nectar',
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='nectar_research_impact',
            field=models.TextField(
                blank=True,
                help_text='Briefly indicate the impact of your research activity that has been supported by Nectar, particularly translational impact (i.e. impact on society).',
                max_length=4096,
                null=True,
                verbose_name='Research Impact',
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='users_figure_type',
            field=models.CharField(
                choices=[('measured', 'Measured'), ('estimated', 'Estimated')],
                default='measured',
                max_length=10,
                null=True,
                verbose_name='Are the above figures measured or estimated?',
            ),
        ),
    ]
