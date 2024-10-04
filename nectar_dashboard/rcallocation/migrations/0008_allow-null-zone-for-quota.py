from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0007_remove-old-zone-fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='status',
            field=models.CharField(
                default=b'N',
                max_length=1,
                choices=[
                    (b'N', b'New'),
                    (b'E', b'Submitted'),
                    (b'A', b'Approved'),
                    (b'R', b'Declined'),
                    (b'X', b'Update requested'),
                    (b'J', b'Update declined'),
                    (b'L', b'Legacy submission'),
                    (b'D', b'Deleted'),
                    (b'M', b'Legacy approved'),
                    (b'O', b'Legacy rejected'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='quota',
            name='zone',
            field=models.ForeignKey(
                blank=True,
                to='rcallocation.Zone',
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
    ]
