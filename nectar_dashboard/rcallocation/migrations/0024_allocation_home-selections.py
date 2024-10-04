from django.db import migrations, models


def set_unassigned_allocation_home(apps, schema_editor):
    AllocationRequest = apps.get_model('rcallocation', 'AllocationRequest')
    for allocation in AllocationRequest.objects.filter(
        requested_allocation_home='national'
    ):
        allocation.requested_allocation_home = 'unassigned'
        allocation.save()


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0023_remove_funding_node'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='allocation_home',
            field=models.CharField(
                choices=[
                    (b'nci', b'Australian Capital Territory (NCI)'),
                    (b'intersect', b'New South Wales (Intersect)'),
                    (b'qcif', b'Queensland (QCIF)'),
                    (b'ersa', b'South Australia (eRSA)'),
                    (b'tpac', b'Tasmania (TPAC)'),
                    (b'uom', b'Victoria (Melbourne)'),
                    (b'monash', b'Victoria (Monash)'),
                    (b'swinburne', b'Victoria (Swinburne)'),
                    (b'auckland', b'Auckland Uni (New Zealand)'),
                    (b'national', b'National'),
                ],
                max_length=128,
                blank=True,
                help_text=b'Allocation home of the allocation',
                null=True,
                verbose_name=b'Allocation Home',
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='nectar_support',
            field=models.CharField(
                help_text=b'Specify any ANDS, Nectar, RDS or ARDC capabilities\n                    supporting this request.',
                max_length=255,
                verbose_name=b'List any ANDS, Nectar, or RDS funded projects supporting this\n        request.',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='requested_allocation_home',
            field=models.CharField(
                default=b'national',
                help_text=b'You can provide a primary location where you expect to\n                use most resources, effectively the main Nectar site for your\n                allocation. Use of other locations is still possible.\n                This can also indicate a specific arrangement with a\n                Nectar site, for example where you obtain support, or if\n                your institution is a supporting member of that site.\n                Select unassigned if you have no preference.\n                ',
                max_length=128,
                verbose_name=b'Allocation home location',
                choices=[
                    (b'unassigned', b'Unassigned'),
                    (b'nci', b'Australian Capital Territory (NCI)'),
                    (b'intersect', b'New South Wales (Intersect)'),
                    (b'qcif', b'Queensland (QCIF)'),
                    (b'ersa', b'South Australia (eRSA)'),
                    (b'tpac', b'Tasmania (TPAC)'),
                    (b'uom', b'Victoria (Melbourne)'),
                    (b'monash', b'Victoria (Monash)'),
                    (b'swinburne', b'Victoria (Swinburne)'),
                    (b'auckland', b'Auckland Uni (New Zealand)'),
                ],
            ),
        ),
        migrations.RunPython(set_unassigned_allocation_home),
    ]
