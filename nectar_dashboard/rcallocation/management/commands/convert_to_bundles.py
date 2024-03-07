import logging

from django.core.management import base

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils


LOG = logging.getLogger(__name__)


class Command(base.BaseCommand):
    help = """Finds Allocations that aren't in a bundle and tries
    to put them in one"""

    def add_arguments(self, parser):
        parser.add_argument('--dry-run',
                            default=False,
                            action='store_true',
                            help="Only print actions")
        parser.add_argument('--allocation',
                            default=None,
                            help="Run on 1 allocation")

    def handle(self, **options):
        dry_run = options.get('dry_run')
        allocation_id = options.get('allocation')

        bundles = models.Bundle.objects.all()

        # Used for dry runs so we get good stats
        ids_with_bundle = []
        totals = {}
        for bundle in bundles:
            count = 0
            if allocation_id:
                allocations = models.AllocationRequest.objects.filter(
                    id=allocation_id,
                    bundle__isnull=True, parent_request__isnull=True)
            else:
                allocations = models.AllocationRequest.objects.filter(
                    bundle__isnull=True, parent_request__isnull=True,
                    managed=True)
                allocations = allocations.exclude(
                    status=models.AllocationRequest.DELETED)
                if dry_run:
                    allocations = allocations.exclude(id__in=ids_with_bundle)

            for allocation in allocations:
                quota_valid = True
                for quota in allocation.quotas.all_quotas():

                    try:
                        bq = bundle.bundlequota_set.get(
                            resource=quota.resource)
                    except models.BundleQuota.DoesNotExist:
                        if quota.resource.service_type.is_multizone():
                            continue
                        quota_valid = False
                        LOG.info(f"{allocation.id}: Resource {quota.resource} "
                                 "does not exist in this bundle")

                    if quota.quota > bq.quota:
                        quota_valid = False
                        LOG.info(
                            f"{allocation.id}: {quota.resource}={quota.quota} "
                            f"bigger than bundle {bq.quota}")

                if quota_valid:
                    LOG.info(f"Allocation {allocation} bundle={bundle}")
                    if not dry_run:
                        utils.copy_allocation(allocation)
                        allocation.bundle = bundle
                        allocation.save_without_updating_timestamps()
                        qg_list = models.QuotaGroup.objects.filter(
                            allocation=allocation, zone=bundle.zone)
                        for qg in qg_list:
                            for q in qg.quota_set.all():
                                q.delete()
                            qg.delete()
                    else:
                        ids_with_bundle.append(allocation.id)

                    count += 1
            LOG.info(f"Bundle {bundle} - {count}")
            totals[bundle] = count
        allocations = models.AllocationRequest.objects.filter(
            bundle__isnull=True, parent_request__isnull=True,
            managed=True)
        allocations = allocations.exclude(
            status=models.AllocationRequest.DELETED)
        if dry_run:
            allocations = allocations.exclude(id__in=ids_with_bundle)
        LOG.info("No Bundle - %s" % allocations.count())
        for b, c in totals.items():
            LOG.info(f"{b}: {c}")
