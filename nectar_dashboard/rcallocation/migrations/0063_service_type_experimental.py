# Generated by Django 2.2.19 on 2022-04-08 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0062_add_servicetype_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='experimental',
            field=models.BooleanField(default=False),
        ),
    ]
