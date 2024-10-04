from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0019_add-notifications-field'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resource',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.CharField(
                default=b'integer',
                max_length=10,
                choices=[(b'integer', b'Integer'), (b'boolean', b'Boolean')],
            ),
        ),
    ]
