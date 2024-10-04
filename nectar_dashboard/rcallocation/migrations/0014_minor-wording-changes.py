from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0013_add-resource-help_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='allocation_home',
            field=models.CharField(
                default=b'national',
                help_text=b'You can provide a primary location where you expect to\n                use most resources, effectively the main Nectar Node for your\n                allocation. Use of other locations is still possible.\n                This can also indicate a specific arrangement with a\n                Nectar Node, for example where you obtain support, or if\n                your institution is a supporting member of that Node.\n                ',
                max_length=128,
                verbose_name=b'Allocation home location',
                choices=[
                    (b'national', b'National/Unassigned'),
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
                verbose_name=b'List any ANDS, Nectar, or RDS funded projects supporting this request.',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='notes',
            field=models.TextField(
                help_text=b'These notes are only visible to allocation admins',
                null=True,
                verbose_name=b'Private notes for admins',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='usage_patterns',
            field=models.TextField(
                help_text=b'Will your project have many users and small data\n        sets? Or will it have large data sets with a small number of users?\n        Will your instances be long running or created and deleted as needed\n        Your answers here will help us.',
                max_length=1024,
                verbose_name=b'Instance, Object Storage and Volumes Storage Usage Patterns',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='allocationrequest',
            name='use_case',
            field=models.TextField(
                help_text=b'Provide a very brief overview of your research project,\n        and how you will use the cloud to support your project.',
                max_length=4096,
                verbose_name=b'Research use case',
            ),
        ),
    ]
