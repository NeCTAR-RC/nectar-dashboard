from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0018_more-grant-type-changes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='allocationrequest',
            options={'ordering': ['-modified_time']},
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='notifications',
            field=models.BooleanField(
                default=True,
                help_text=b'Send notifications for this allocation',
            ),
        ),
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
                    (b'L', b'Legacy submission'),
                    (b'D', b'Deleted'),
                    (b'M', b'Legacy approved'),
                    (b'O', b'Legacy rejected'),
                ],
            ),
        ),
    ]
