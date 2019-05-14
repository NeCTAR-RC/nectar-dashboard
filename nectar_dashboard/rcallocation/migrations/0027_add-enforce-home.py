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
    ]
