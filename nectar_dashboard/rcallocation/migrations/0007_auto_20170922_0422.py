# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0006_convert-quota-keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([('allocation', 'resource', 'zone')]),
        ),
    ]
