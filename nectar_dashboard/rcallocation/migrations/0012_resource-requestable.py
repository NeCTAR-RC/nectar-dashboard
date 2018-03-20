# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


def set_ram_unrequestable(apps, schema_editor):
    Resource = apps.get_model('rcallocation', 'Resource')
    try:
        ram = Resource.objects.get(quota_name='ram')
        ram.requestable = False
        ram.save()
    except Resource.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0011_add-quota-groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='requestable',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(set_ram_unrequestable),
    ]
