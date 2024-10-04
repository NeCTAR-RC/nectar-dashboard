from django.db import migrations, models

DUMMY_SERVICE_TYPE = 'oaxoo7ItoiRu9naidaeteekai5ianei1'


def create_dummy_group(apps, schema_editor):
    QuotaGroup = apps.get_model('rcallocation', 'QuotaGroup')
    AllocationRequest = apps.get_model('rcallocation', 'AllocationRequest')
    ServiceType = apps.get_model('rcallocation', 'ServiceType')
    Zone = apps.get_model('rcallocation', 'Zone')
    try:
        allocation = AllocationRequest.objects.all()[0]
    except IndexError:
        return
    zone = Zone.objects.create(
        name=DUMMY_SERVICE_TYPE, display_name=DUMMY_SERVICE_TYPE
    )
    st = ServiceType.objects.create(
        name=DUMMY_SERVICE_TYPE, catalog_name=DUMMY_SERVICE_TYPE
    )

    QuotaGroup.objects.create(
        id=1, allocation=allocation, service_type=st, zone=zone
    )


def delete_dummy_group(apps, schema_editor):
    QuotaGroup = apps.get_model('rcallocation', 'QuotaGroup')
    AllocationRequest = apps.get_model('rcallocation', 'AllocationRequest')
    try:
        AllocationRequest.objects.all()[0]
    except IndexError:
        return

    qg = QuotaGroup.objects.get(id=1)
    st = qg.service_type
    zone = qg.zone
    qg.delete()
    st.delete()
    zone.delete()


def convert_quotas(apps, schema_editor):
    QuotaGroup = apps.get_model('rcallocation', 'QuotaGroup')
    Quota = apps.get_model('rcallocation', 'Quota')

    for quota in Quota.objects.all():
        qg, created = QuotaGroup.objects.get_or_create(
            allocation=quota.allocation,
            service_type=quota.resource.service_type,
            zone=quota.zone,
        )
        quota.group = qg
        quota.save()


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0010_convert-compute-quota'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotaGroup',
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
            ],
        ),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([]),
        ),
        migrations.AddField(
            model_name='quotagroup',
            name='allocation',
            field=models.ForeignKey(
                related_name='quotas',
                to='rcallocation.AllocationRequest',
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name='quotagroup',
            name='service_type',
            field=models.ForeignKey(
                to='rcallocation.ServiceType', on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='quotagroup',
            name='zone',
            field=models.ForeignKey(
                to='rcallocation.Zone', on_delete=models.CASCADE
            ),
        ),
        migrations.RunPython(create_dummy_group),
        migrations.AddField(
            model_name='quota',
            name='group',
            field=models.ForeignKey(
                default=1,
                to='rcallocation.QuotaGroup',
                on_delete=models.CASCADE,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(convert_quotas),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([('group', 'resource')]),
        ),
        migrations.RemoveField(
            model_name='quota',
            name='allocation',
        ),
        migrations.RemoveField(
            model_name='quota',
            name='zone',
        ),
        migrations.AlterUniqueTogether(
            name='quotagroup',
            unique_together=set([('allocation', 'zone', 'service_type')]),
        ),
        migrations.RunPython(delete_dummy_group),
    ]
