# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0012_resource-requestable'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='help_text',
            field=models.TextField(null=True, blank=True),
        ),
    ]
