# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0003_add-provisioned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='status',
            field=models.CharField(default=b'N', max_length=1, choices=[(b'N', b'New'), (b'E', b'Submitted'), (b'A', b'Approved'), (b'R', b'Declined'), (b'X', b'Update/extension requested'), (b'J', b'Update/extension declined'), (b'L', b'Legacy submission'), (b'M', b'Legacy approved'), (b'O', b'Legacy rejected')]),
        ),
        migrations.AlterField(
            model_name='quota',
            name='resource',
            field=models.CharField(max_length=64, choices=[(b'volume', b'Volume storage'), (b'object', b'Object storage'), (b'database.instances', b'Database servers'), (b'database.volumes', b'Database storage')]),
        ),
        migrations.AlterField(
            model_name='quota',
            name='units',
            field=models.CharField(default=b'GB', max_length=64, verbose_name=b'The units the quota is stored in.', blank=True),
        ),
    ]
