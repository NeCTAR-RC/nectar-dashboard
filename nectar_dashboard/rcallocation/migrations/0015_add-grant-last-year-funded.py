from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0014_minor-wording-changes'),
    ]

    operations = [
        migrations.AddField(
            model_name='grant',
            name='last_year_funded',
            field=models.IntegerField(
                default=2019,
                help_text=b'Specify the last year funded',
                error_messages={
                    b'max_value': b'Please input a year between 1970 ~ 3000',
                    b'min_value': b'Please input a year between 1970 ~ 3000',
                },
                verbose_name=b'Last year funded',
                validators=[
                    django.core.validators.MinValueValidator(1970),
                    django.core.validators.MaxValueValidator(3000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='grant',
            name='first_year_funded',
            field=models.IntegerField(
                default=2018,
                help_text=b'Specify the first year funded',
                error_messages={
                    b'max_value': b'Please input a year between 1970 ~ 3000',
                    b'min_value': b'Please input a year between 1970 ~ 3000',
                },
                verbose_name=b'First year funded',
                validators=[
                    django.core.validators.MinValueValidator(1970),
                    django.core.validators.MaxValueValidator(3000),
                ],
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
                    (b'nectar', b'Nectar funding'),
                    (b'ands', b'ANDS funding'),
                    (b'govt', b'Other Australian government grant'),
                    (b'industry', b'Industry funding'),
                    (b'ext', b'Other external funding'),
                    (b'inst', b'Institutional research grant'),
                ],
            ),
        ),
    ]
