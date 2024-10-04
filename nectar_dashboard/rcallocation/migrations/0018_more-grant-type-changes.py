from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0017_grant-type-change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grant',
            name='grant_type',
            field=models.CharField(
                default=b'arc',
                help_text=b'Choose the grant type from the dropdown options.',
                max_length=128,
                verbose_name=b'Type',
                choices=[
                    (b'arc', b'ARC'),
                    (b'comp', b'Other Australian Competitive Grants'),
                    (b'ncris', b'NCRIS funding'),
                    (
                        b'ands_nectar_rds',
                        b'Funded by ARDC, Nectar, ANDS or RDS',
                    ),
                    (b'nhmrc', b'NHMRC'),
                    (b'govt', b'Other Australian government grant'),
                    (b'industry', b'Industry funding'),
                    (b'ext', b'Other external funding'),
                    (b'inst', b'Institutional research grant'),
                ],
            ),
        ),
    ]
