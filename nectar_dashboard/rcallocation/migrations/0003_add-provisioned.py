from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0002_minor-field-mods'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocationrequest',
            name='provisioned',
            field=models.BooleanField(default=False),
        ),
    ]
