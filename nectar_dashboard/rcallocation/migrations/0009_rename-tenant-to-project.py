# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0008_remove-old-zone-fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='allocationrequest',
            old_name='tenant_uuid',
            new_name='project_id',
        ),
        migrations.RenameField(
            model_name='allocationrequest',
            old_name='project_name',
            new_name='project_description',
        ),
        migrations.RenameField(
            model_name='allocationrequest',
            old_name='tenant_name',
            new_name='project_name',
        ),
    ]
