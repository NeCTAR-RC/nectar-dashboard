# Generated by Django 3.2.18 on 2024-03-14 23:34

from django.db import migrations
from django.db import models

import nectar_dashboard.rcallocation.models


SU_CODENAME = 'rating.budget'


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0075_remove_unknown_org'),
    ]

    def populate_su_per_year(apps, schema_editor):
        Bundle = apps.get_model('rcallocation', 'Bundle')
        BundleQuota = apps.get_model('rcallocation', 'BundleQuota')
        Resource = apps.get_model('rcallocation', 'Resource')
        try:
            resource = Resource.objects.get_by_codename(SU_CODENAME)
        except Exception as e:
            print(e)
            return
        for bundle in Bundle.objects.all():
            try:
                bq = BundleQuota.objects.get(bundle=bundle, resource=resource)
            except Exception as e:
                print(e)
                continue
            else:
                su_budget = bq.quota
            if su_budget:
                bundle.su_per_year = su_budget
                bundle.save()

            bqs = bundle.bundlequota_set.filter(resource=resource)
            for bq in bqs:
                bq.delete()

    def reverse_populate_su_per_year(apps, schema_editor):
        Bundle = apps.get_model('rcallocation', 'Bundle')
        BundleQuota = apps.get_model('rcallocation', 'BundleQuota')
        Resource = apps.get_model('rcallocation', 'Resource')
        try:
            resource = Resource.objects.get_by_codename(SU_CODENAME)
        except Exception:
            return

        for bundle in Bundle.objects.all():
            su_budget = bundle.su_per_year
            BundleQuota.objects.create(
                bundle=bundle, resource=resource, quota=su_budget)

    operations = [
        migrations.AlterModelManagers(
            name='resource',
            managers=[
                ('objects',
                 nectar_dashboard.rcallocation.models.ResourceManager()),
            ],
        ),
        migrations.AddField(
            model_name='bundle',
            name='su_per_year',
            field=models.IntegerField(
                null=True, verbose_name='SU budget per year'),
        ),

        migrations.RunPython(populate_su_per_year,
                             reverse_populate_su_per_year),

        migrations.AlterField(
            model_name='bundle',
            name='su_per_year',
            field=models.IntegerField(
                default=0, verbose_name='SU budget per year'),
            preserve_default=False,
        ),
    ]
