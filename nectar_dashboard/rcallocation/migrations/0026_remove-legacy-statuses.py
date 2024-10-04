from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0025_allocation_home-set-national'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationrequest',
            name='status',
            field=models.CharField(
                default=b'E',
                max_length=1,
                choices=[
                    (b'N', b'New'),
                    (b'E', b'Submitted'),
                    (b'A', b'Approved'),
                    (b'R', b'Declined'),
                    (b'X', b'Update requested'),
                    (b'J', b'Update declined'),
                    (b'D', b'Deleted'),
                ],
            ),
        ),
    ]
