# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0021_servicetype_notes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='allocationrequest',
            old_name='allocation_home',
            new_name='requested_allocation_home',
        ),
    ]
