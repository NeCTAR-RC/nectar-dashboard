from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0003_add-provisioned'),
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
