import logging

from django.core.management.base import BaseCommand
from nectar_dashboard.rcallocation import models


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Hard delete an allocation request and associated records.  "
        "Use carefully as there is no undo."
    )

    def add_arguments(self, parser):
        parser.add_argument('allocation', help="The allocation id")
        parser.add_argument(
            '--no-dry-run', action="store_true", help="If set, do the delete"
        )
        parser.add_argument(
            '--history',
            action="store_true",
            help="If set, just delete a single history "
            "record.  Otherwise delete an allocation and "
            "all of its history.",
        )

    def handle(self, allocation, **options):
        dry_run = not options["no_dry_run"]
        self.delete_allocation(
            allocation, dry_run=dry_run, history=options["history"]
        )

    def _summary(self, allocation):
        type = "history" if allocation.parent_request else "parent"
        return (
            f"{type} record {allocation.id}, "
            f"project name: {allocation.project_name}, "
            f"project id: {allocation.project_id}, "
            f"status: {allocation.status}, "
            f"last update: {allocation.modified_time}"
        )

    def delete_allocation(self, id, dry_run=True, history=False):
        """Hard delete an allocation record with a given 'id'
        - if history=True 'id' is expected to be a history record
        - if history=False 'id' is expected to be a master (parent) record
          and all associated history records will be deleted.
        Component records should be cascade deleted by the database.
        """

        try:
            allocation = models.AllocationRequest.objects.get(id=id)
        except models.AllocationRequest.DoesNotExist:
            print(f"Allocation with id {id} not found")
            return

        allocations = [allocation]
        if allocation.parent_request:
            if not history:
                print(
                    f"Allocation record {id} is a history record "
                    f"for allocation {allocation.parent_request.id}"
                )
                return
        else:
            if history:
                print(f"Allocation record {id} is a not history record")
                return

        # Build list of allocation records be deleted
        for h in models.AllocationRequest.objects.filter(
            parent_request=allocation
        ):
            allocations.append(h)

        if not dry_run:
            # Delete history records before the parent.  It is safer.
            for a in reversed(allocations):
                LOG.info(f"Hard deleting allocation: {self._summary(a)}")
                a.delete()
        else:
            for a in allocations:
                print(f"Would delete allocation: {self._summary(a)}")
