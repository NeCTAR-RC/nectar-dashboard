from django.db import migrations


class Migration(migrations.Migration):
    def upgrade(apps, schema_editor):
        NCRISFacility = apps.get_model('rcallocation', 'NCRISFacility')
        try:
            appn = NCRISFacility.objects.get(short_name="APPF")
        except NCRISFacility.DoesNotExist:
            pass
        else:
            appn.short_name = "APPN"
            appn.name = "Australian Plant Phenomics Network"
            appn.save()

    def downgrade(apps, schema_editor):
        pass

    dependencies = [
        ('rcallocation', '0082_alter_allocationrequest_contact_email'),
    ]

    operations = [migrations.RunPython(upgrade, downgrade)]
