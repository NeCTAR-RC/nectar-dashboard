from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0022_requested_allocation_home'),
    ]

    operations = [
        migrations.RenameField(
            model_name='allocationrequest',
            old_name='funding_node',
            new_name='allocation_home',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='funding_national_percent',
        ),
    ]
