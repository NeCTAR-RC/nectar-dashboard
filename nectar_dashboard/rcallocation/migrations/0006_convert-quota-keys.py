from django.db import migrations, models


def convert_resource(apps, schema_editor):
    Resource = apps.get_model('rcallocation', 'Resource')
    Quota = apps.get_model('rcallocation', 'Quota')

    resource_cache = {}
    for quota in Quota.objects.all():
        if '.' in quota.resource:
            orig_resource = quota.resource.split('.')[1]
        else:
            orig_resource = quota.resource
        if orig_resource in resource_cache:
            resource_id = resource_cache[orig_resource]
        else:
            resource = Resource.objects.get(quota_name=orig_resource)
            resource_cache[orig_resource] = resource.id
            resource_id = resource.id

        quota.resource_id = resource_id
        quota.save()


class Migration(migrations.Migration):
    dependencies = [
        ('rcallocation', '0005_add-service-type-zone-resource-tables'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=(),
        ),
        migrations.AddField(
            model_name='quota',
            name='resource_id',
            field=models.IntegerField(),
        ),
        migrations.RunPython(convert_resource),
        migrations.RemoveField(
            model_name='quota',
            name='resource',
        ),
        migrations.RenameField(
            model_name='quota',
            old_name='resource_id',
            new_name='resource',
        ),
        migrations.AlterField(
            model_name='quota',
            name='resource',
            field=models.ForeignKey(
                to='rcallocation.Resource', on_delete=models.CASCADE
            ),
        ),
        migrations.AlterField(
            model_name='quota',
            name='zone',
            field=models.ForeignKey(
                to='rcallocation.Zone', on_delete=models.CASCADE
            ),
        ),
        migrations.AlterField(
            model_name='zone',
            name='display_name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([('allocation', 'resource', 'zone')]),
        ),
        migrations.RemoveField(
            model_name='quota',
            name='units',
        ),
    ]
