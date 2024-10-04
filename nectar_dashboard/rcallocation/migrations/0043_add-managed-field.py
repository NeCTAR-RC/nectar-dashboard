from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0042_support_and_grant_tweaks'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocationrequest',
            name='managed',
            field=models.BooleanField(
                default=True,
                help_text=b'Whether the allocation is managed through the dashboard',
            ),
        ),
    ]
