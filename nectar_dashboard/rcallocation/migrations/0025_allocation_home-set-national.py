from django.db import migrations


def set_national_allocation_home(apps, schema_editor):
    AllocationRequest = apps.get_model('rcallocation', 'AllocationRequest')
    for allocation in AllocationRequest.objects.filter(
        allocation_home__isnull=True
    ):
        allocation.allocation_home = 'national'
        allocation.save()


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0024_allocation_home-selections'),
    ]

    operations = [migrations.RunPython(set_national_allocation_home)]
