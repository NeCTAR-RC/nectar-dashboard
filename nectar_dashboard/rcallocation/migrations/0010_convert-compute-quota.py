from django.db import migrations


def migrate_compute_quota(apps, schema_editor):
    AllocationRequest = apps.get_model('rcallocation', 'AllocationRequest')
    Quota = apps.get_model('rcallocation', 'Quota')
    Zone = apps.get_model('rcallocation', 'Zone')
    Resource = apps.get_model('rcallocation', 'Resource')
    ServiceType = apps.get_model('rcallocation', 'ServiceType')

    zone, created = Zone.objects.get_or_create(
        name='nectar', defaults={'display_name': 'Nectar'}
    )
    st, created = ServiceType.objects.get_or_create(
        catalog_name='compute', defaults={'name': 'Compute Service'}
    )
    st.zones.add(zone)
    core_resource, created = Resource.objects.get_or_create(
        quota_name='cores',
        service_type=st,
        defaults={
            'unit': 'VCPUs',
            'name': 'Virtual Cores',
            'service_type': st,
        },
    )

    ram_resource, created = Resource.objects.get_or_create(
        quota_name='ram',
        service_type=st,
        defaults={'unit': 'GB', 'name': 'RAM', 'service_type': st},
    )

    instance_resource, created = Resource.objects.get_or_create(
        quota_name='instances',
        service_type=st,
        defaults={'unit': 'servers', 'name': 'Instances', 'service_type': st},
    )

    for allocation in AllocationRequest.objects.all():
        Quota.objects.create(
            allocation=allocation,
            zone=zone,
            resource=instance_resource,
            quota=allocation.instance_quota,
            requested_quota=allocation.instances,
        )
        Quota.objects.create(
            allocation=allocation,
            zone=zone,
            resource=ram_resource,
            quota=allocation.ram_quota,
            requested_quota=allocation.ram_quota,
        )
        Quota.objects.create(
            allocation=allocation,
            zone=zone,
            resource=core_resource,
            quota=allocation.core_quota,
            requested_quota=allocation.cores,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0009_add-admin-nodes-field'),
    ]

    operations = [
        migrations.RunPython(migrate_compute_quota),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='core_hours',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='core_quota',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='cores',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='instance_quota',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='instances',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='primary_instance_type',
        ),
        migrations.RemoveField(
            model_name='allocationrequest',
            name='ram_quota',
        ),
    ]
