# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0026_remove-legacy-statuses'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocationrequest',
            name='enforce_home',
            field=models.BooleanField(default=False, help_text=b'Enforce allocation home on a project'),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='use_case',
            field=models.TextField(help_text=b'Provide a very brief overview of your research project,\n        and how you will use the cloud to support your project.', max_length=4096, verbose_name=b'Research use case and justification'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='first_year_funded',
            field=models.IntegerField(default=2019, help_text=b'Specify the first year funded', error_messages={b'max_value': b'Please input a year between 1970 ~ 3000', b'min_value': b'Please input a year between 1970 ~ 3000'}, verbose_name=b'First year funded', validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)]),
        ),
        migrations.AlterField(
            model_name='grant',
            name='last_year_funded',
            field=models.IntegerField(default=2020, help_text=b'Specify the last year funded', error_messages={b'max_value': b'Please input a year between 1970 ~ 3000', b'min_value': b'Please input a year between 1970 ~ 3000'}, verbose_name=b'Last year funded', validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)]),
        ),
    ]
