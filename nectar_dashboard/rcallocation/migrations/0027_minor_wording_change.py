# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0026_remove-legacy-statuses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='use_case',
            field=models.TextField(help_text=b'Provide a very brief overview of your research project,\n        and how you will use the cloud to support your project.', max_length=4096, verbose_name=b'Research use case and justification'),
        ),
    ]
