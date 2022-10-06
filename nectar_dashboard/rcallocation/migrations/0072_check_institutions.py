# Generated by Django 2.2.12 on 2023-04-04 22:59

import logging

from django.db import migrations


LOG = logging.getLogger(__name__)


class Migration(migrations.Migration):
    """Check that there is a non-NULL supported Organisation for all 
    AllocationRequest records, and a non-NULL primary_organization for
    all ChiefInvestigator records.  The next migration will switch the
    corresponding fields to 'blank=False, null=False'.  (The backfilling
    is done using the 'migrate_organisations' admin command.)
    """

    def check(apps, schema_editor):
        AllocationRequest = apps.get_model('rcallocation', 'AllocationRequest')
        ChiefInvestigator = apps.get_model('rcallocation', 'ChiefInvestigator')
        allocations_with_no_orgs = AllocationRequest.objects \
                                    .filter(supported_organisations=None)
        if alloc_count := allocations_with_no_orgs.count():
            LOG.error(f"Found {alloc_count} AllocationRequest records with "
                      "no supported organisations.")
        cis_with_no_orgs = ChiefInvestigator.objects \
                                    .filter(primary_organisation=None)
        if ci_count := cis_with_no_orgs.count():
            LOG.error(f"Found {ci_count} ChiefInvestigator records with "
                      "no primary organisation.")
        if alloc_count or ci_count:
            raise Exception("Detected NULL Organisation fields.")

    def noop(apps, schema_editor):
        pass

    dependencies = [
        ('rcallocation', '0071_convert_institutions'),
    ]

    operations = [
        migrations.RunPython(check, reverse_code=noop) 
    ]
