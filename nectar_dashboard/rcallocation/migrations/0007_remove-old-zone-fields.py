# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0006_convert-quota-keys'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allocationrequest',
            name='object_storage_zone',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='volume_zone',
        ),
    ]
