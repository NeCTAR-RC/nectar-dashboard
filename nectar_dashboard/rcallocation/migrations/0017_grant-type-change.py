from django.db import migrations, models


def migrate_grant_types(apps, schema_editor):
    Grant = apps.get_model('rcallocation', 'Grant')

    for grant in Grant.objects.all():
        if grant.grant_type in ['nectar', 'ands']:
            grant.grant_type = 'ands_nectar_rds'
            grant.save()


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0016_minor-wording-changes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='geographic_requirements',
            field=models.TextField(
                help_text=b'Indicate to the allocations committee any special\n                geographic requirements that you may need, e.g. to run\n                at more than one node.',
                max_length=1024,
                verbose_name=b'Additional location requirements',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='grant',
            name='grant_type',
            field=models.CharField(
                default=b'arc',
                help_text=b'Choose the grant type from the dropdown options.',
                max_length=128,
                verbose_name=b'Type',
                choices=[
                    (b'comp', b'Australian competitive research grant'),
                    (b'ncris', b'NCRIS funding'),
                    (b'ands_nectar_rds', b'ANDS, Nectar, RDS funding'),
                    (b'nhmrc', b'NHMRC'),
                    (b'govt', b'Other Australian government grant'),
                    (b'industry', b'Industry funding'),
                    (b'ext', b'Other external funding'),
                    (b'inst', b'Institutional research grant'),
                ],
            ),
        ),
        migrations.AlterUniqueTogether(
            name='publication',
            unique_together=set([]),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication',
            field=models.CharField(
                help_text=b'Please provide any traditional and non-traditional\n                research outputs using a citation style text reference\n                for each. eg. include article/title, journal/outlet, year,\n                DOI/link if available.',
                max_length=512,
                verbose_name=b'Publication/Output',
            ),
        ),
        migrations.RunPython(migrate_grant_types),
    ]
