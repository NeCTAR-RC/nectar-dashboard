import logging

from django.core import exceptions
from django.core.management.base import BaseCommand

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Replace one Organisation with another one.  This will replace "
        "all usages of the original Organisation with the replacement in "
        "all Allocation and ChiefInvestigator records.  The original "
        "Organisation may then be marked as disabled."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'original', help="ROR or local id of original Organisation"
        )
        parser.add_argument(
            'replacement', help="ROR or local id of replacement Organisation"
        )
        parser.add_argument(
            '--disable',
            action="store_true",
            help="Disable the original Organisation after " "replacing it",
        )
        parser.add_argument(
            '--no-dry-run',
            action="store_true",
            help="If set, perform the replacement. "
            "Otherwise just show the details of the "
            "Organisations, and list the Allocation and CI "
            "records affected",
        )

    def handle(self, original, replacement, **options):
        original_org = self.lookup_org(original)
        replacement_org = self.lookup_org(replacement)
        if not original_org or not replacement_org:
            return

        if original_org.pk == replacement_org.pk:
            print(
                f"Ids ({original} and {replacement}) "
                "refer to the same Organisation"
            )
            return

        print("== Original Organisation =====")
        self.show_organisation(original_org)
        print("== Replacement Organisation ==")
        self.show_organisation(replacement_org)
        print("==============================")

        if not replacement_org.enabled:
            print("Warning: the replacement Organisation is disabled")

        self.replace_organisations(
            original_org, replacement_org, no_dry_run=options['no_dry_run']
        )
        if options['disable'] and original_org.enabled:
            if options['no_dry_run']:
                original_org.enabled = False
                original_org.save()
                LOG.info(f"Disabled Organisation {original_org.id}")
            else:
                print(f"Would disable Organisation {original_org.id}")

    def lookup_org(self, key):
        try:
            if key.isdigit():
                return models.Organisation.objects.get(id=int(key))
            elif key.startswith("https://"):
                return models.Organisation.objects.get(ror_id=key)
            else:
                return models.Organisation.objects.get(
                    short_name=key, ror_id=''
                )
        except exceptions.DoesNotExist:
            print(f"Can't find an Organisation with id {key}")
            return None

    def replace_organisations(
        self, original_org, replacement_org, no_dry_run=False
    ):
        for a in models.AllocationRequest.objects.filter(
            supported_organisations=original_org
        ):
            if no_dry_run:
                a.supported_organisations.add(replacement_org)
                a.supported_organisations.remove(original_org)
                utils.save_allocation_without_updating_timestamps(a)
                LOG.info(
                    f"Changed Organisation {original_org.id} "
                    f"to {replacement_org.id} for allocation {a.id}"
                )
            else:
                print(f"Would change Organisation for allocation {a.id}")

        for ci in models.ChiefInvestigator.objects.filter(
            primary_organisation=original_org
        ):
            if no_dry_run:
                ci.primary_organisation = replacement_org
                ci.save()
                LOG.info(
                    f"Changed Organisation {original_org.id} "
                    f"to {replacement_org.id} for CI {ci.id}"
                )
            else:
                print(f"Would change Organisation for CI {ci.id}")

    def show_organisation(self, org):
        print(f"id: {org.id}, ror_id: {org.ror_id}")
        print(f"short_name: {org.short_name}")
        print(f"full_name: {org.full_name}")
        print(f"country: {org.country}, enabled: {org.enabled}")
        if org.proposed_by:
            print(f"              proposed_by: {org.proposed_by}")
        if org.vetted_by:
            print(f"              vetted_by: {org.vetted_by.username}")
