# Generated by Django 1.11.11 on 2020-11-30 07:15

import logging

from django.db import migrations


LOG = logging.getLogger(__name__)


class Migration(migrations.Migration):
    def expunge(apps, schema_editor):
        apps.get_model('rcallocation', 'AllocationRequest')
        Grant = apps.get_model('rcallocation', 'Grant')
        errors = 0
        for grant in Grant.objects.all():
            if grant.grant_type not in ['ncris', 'ands_nectar_rds']:
                continue

            # We are not expunging ARDC / NCRIS "grants" from the
            # allocation history.  It is too messy.
            allocation = grant.allocation
            if allocation.parent_request_id is not None:
                continue

            # We should have (manually) put something in the ARDC / NCRIS
            # support fields corresponding to grants to be expunged.
            # Check.  (It won't be one-to-one in all cases ...)
            if allocation.nectar_support or allocation.ncris_support:
                grant.delete()
                print(
                    f"Deleting grant {grant.id} for allocation {allocation.id}"
                )
            else:
                errors += 1
                print(
                    "You haven't set the support field(s) for"
                    f" allocation {allocation.id}"
                )

        if errors > 0:
            raise Exception(
                'Abandoning migration: see earlier output ' 'for the errors'
            )

    dependencies = [
        ('rcallocation', '0047_remove_grant_type_choices'),
    ]

    operations = [
        migrations.RunPython(expunge, reverse_code=None)  # not reversible
    ]
