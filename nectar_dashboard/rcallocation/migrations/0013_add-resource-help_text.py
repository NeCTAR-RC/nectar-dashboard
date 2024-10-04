from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0012_resource-requestable'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='help_text',
            field=models.TextField(null=True, blank=True),
        ),
    ]
