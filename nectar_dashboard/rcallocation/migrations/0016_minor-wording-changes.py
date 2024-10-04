from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0015_add-grant-last-year-funded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='allocation_home',
            field=models.CharField(
                default=b'national',
                help_text=b'You can provide a primary location where you expect to\n                use most resources, effectively the main Nectar site for your\n                allocation. Use of other locations is still possible.\n                This can also indicate a specific arrangement with a\n                Nectar site, for example where you obtain support, or if\n                your institution is a supporting member of that site.\n                Select unassigned if you have no preference.\n                ',
                max_length=128,
                verbose_name=b'Allocation home location',
                choices=[
                    (b'national', b'Unassigned'),
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
        migrations.AlterField(
            model_name='allocationrequest',
            name='nectar_support',
            field=models.CharField(
                max_length=255,
                verbose_name=b'List any ANDS, Nectar, or RDS funded projects supporting this\n        request.',
                blank=True,
            ),
        ),
    ]
