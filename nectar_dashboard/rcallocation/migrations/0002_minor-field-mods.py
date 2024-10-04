from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='allocation_home',
            field=models.CharField(
                default=b'national',
                help_text=b'You can provide a primary location where you expect to\n                use most resources, effectively the main NeCTAR node for your\n                allocation. Use of other locations is still possible.\n                This can also indicate a specific arrangement with a\n                NeCTAR Node, for example where you obtain support, or if\n                your institution is a supporting member of that Node.\n                ',
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
            name='funding_node',
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
                ],
                max_length=128,
                blank=True,
                help_text=b'You can choose the node that complements\n                    the National Funding.',
                null=True,
                verbose_name=b'Node Funding Remainder (if applicable)',
            ),
        ),
        migrations.AlterField(
            model_name='grant',
            name='first_year_funded',
            field=models.IntegerField(
                default=2017,
                help_text=b'Specify the first year funded',
                error_messages={
                    b'max_value': b'Please input a year between 1970 ~ 3000',
                    b'min_value': b'Please input a year between 1970 ~ 3000',
                },
                verbose_name=b'First year funded',
                validators=[
                    django.core.validators.MinValueValidator(1970),
                    django.core.validators.MaxValueValidator(3000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='quota',
            name='quota',
            field=models.PositiveIntegerField(
                default=b'0', verbose_name=b'Allocated quota'
            ),
        ),
        migrations.AlterField(
            model_name='quota',
            name='requested_quota',
            field=models.PositiveIntegerField(
                default=b'0', verbose_name=b'Requested quota'
            ),
        ),
    ]
