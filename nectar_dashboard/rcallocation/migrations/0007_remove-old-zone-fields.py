from django.db import migrations


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
