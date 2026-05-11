from django.db import migrations


class Migration(migrations.Migration):
    def upgrade(apps, schema_editor):
        ServiceType = apps.get_model('rcallocation', 'ServiceType')

        # Mark services that today render in Location Specific Resources
        # because they happen to have multiple zones. The form now uses
        # this flag rather than zone count to decide.
        ServiceType.objects.filter(
            catalog_name__in=['volume', 'share']
        ).update(location_specific=True)

    def downgrade(apps, schema_editor):
        ServiceType = apps.get_model('rcallocation', 'ServiceType')
        ServiceType.objects.filter(
            catalog_name__in=['volume', 'share']
        ).update(location_specific=False)

    dependencies = [
        ('rcallocation', '0086_servicetype_location_specific'),
    ]

    operations = [migrations.RunPython(upgrade, downgrade)]
