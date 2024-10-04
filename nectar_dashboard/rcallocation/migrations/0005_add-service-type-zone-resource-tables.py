from django.conf import settings
from django.db import migrations, models


def populate_zone_and_resources(apps, schema_editor):
    Zone = apps.get_model('rcallocation', 'Zone')
    Resource = apps.get_model('rcallocation', 'Resource')
    ServiceType = apps.get_model('rcallocation', 'ServiceType')

    for quota_type, azs in getattr(
        settings, 'ALLOCATION_QUOTA_AZ_CHOICES', {}
    ).items():
        service_type_name = quota_type.split('.')[0]
        service_type, created = ServiceType.objects.get_or_create(
            catalog_name=service_type_name, name=service_type_name
        )
        for name, display_name in azs:
            zone, created = Zone.objects.get_or_create(
                name=name, display_name=display_name
            )
            service_type.zones.add(zone)

    quota_units = getattr(settings, 'ALLOCATION_QUOTA_UNITS', {})
    for quota_type in getattr(settings, 'ALLOCATION_QUOTA_TYPES', ()):
        service_type, name = quota_type
        unit = quota_units[service_type]
        quota_name = service_type
        if '.' in service_type:
            service_type, quota_name = service_type.split('.')

        service_type = ServiceType.objects.get(name=service_type)
        Resource.objects.get_or_create(
            name=name,
            service_type=service_type,
            quota_name=quota_name,
            unit=unit,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0004_rename-tenant-to-project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ('name', models.CharField(max_length=64)),
                ('quota_name', models.CharField(max_length=32)),
                ('unit', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                (
                    'catalog_name',
                    models.CharField(
                        max_length=32, serialize=False, primary_key=True
                    ),
                ),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                (
                    'name',
                    models.CharField(
                        max_length=32, serialize=False, primary_key=True
                    ),
                ),
                ('display_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='servicetype',
            name='zones',
            field=models.ManyToManyField(to='rcallocation.Zone'),
        ),
        migrations.AddField(
            model_name='resource',
            name='service_type',
            field=models.ForeignKey(
                to='rcallocation.ServiceType', on_delete=models.CASCADE
            ),
        ),
        migrations.AlterUniqueTogether(
            name='resource',
            unique_together=set([('service_type', 'quota_name')]),
        ),
        migrations.RunPython(populate_zone_and_resources),
    ]
