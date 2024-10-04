from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0027_minor_wording_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grant',
            name='first_year_funded',
            field=models.IntegerField(
                default=2019,
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
            name='last_year_funded',
            field=models.IntegerField(
                default=2020,
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
    ]
