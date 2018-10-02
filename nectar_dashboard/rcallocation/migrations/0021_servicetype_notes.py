# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0020_resource_resource_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
