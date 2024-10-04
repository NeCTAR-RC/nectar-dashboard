from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0008_allow-null-zone-for-quota'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocationrequest',
            name='notes',
            field=models.TextField(
                null=True, verbose_name=b'Private notes for admins', blank=True
            ),
        ),
    ]
