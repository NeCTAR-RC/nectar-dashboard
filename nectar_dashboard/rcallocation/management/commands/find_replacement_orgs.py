import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

from nectar_dashboard.rcallocation.management import catalogs

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scan for active local (non-ROR) Organisation records that seem " \
        "to be subsumed by records from the ROR.  For each potential hit, " \
        "print the details of the local Organisation folllowed by the " \
        "ROR Organisations that seem to match."

    def add_arguments(self, parser):
        pass

    def handle(self, **options):
        catalog = catalogs.make_current_catalog()
        verbose = options['verbosity'] > 1
        for o in catalog.Organisation.objects.filter(
                ror_id="", enabled=True):
            candidates = catalog.Organisation.objects \
                                .exclude(ror_id="") \
                                .filter(country=o.country) \
                                .filter(Q(short_name__iexact=o.short_name)
                                        | Q(full_name__iexact=o.full_name))
            if c := candidates.count():
                print(f"Local Organisation {o.id} potentially matches "
                      f"{c} ROR Organisation{'s' if c > 1 else ''}")
                print("-- Local Organisation --")
                self.show_organisation(o)
                for r in candidates:
                    print("--- ROR Organisation ---")
                    self.show_organisation(r)
                print("========================")
            elif verbose:
                print(f"Local Organisation {o.id} ({o.full_name}) "
                      "does not match")
                print("========================")

    def show_organisation(self, org):
        print(f"id: {org.id}, ror_id: {org.ror_id}")
        print(f"short_name: {org.short_name}")
        print(f"full_name: {org.full_name}")
        print(f"country: {org.country}, enabled: {org.enabled}")
        if org.proposed_by:
            print(f"              proposed_by: {org.proposed_by}")
        if org.vetted_by:
            print(f"              vetted_by: {org.vetted_by.username}")
