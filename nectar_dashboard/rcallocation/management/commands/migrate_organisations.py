import itertools
import logging

from django.core.management.base import BaseCommand

from nectar_dashboard.rcallocation.management import catalogs
from nectar_dashboard.rcallocation.management import org_matching


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Organisation migration tool'

    def add_arguments(self, parser):
        parser.add_argument('filename',
                            help="The ROR dump file pathname")
        parser.add_argument('--migrate', action='store_true',
                            help='Perform the data migration')
        parser.add_argument('--check', action='store_true',
                            help='Check mapping rules')
        parser.add_argument('--nonstrict', action='store_true',
                            help='Disable strict mapping')
        parser.add_argument('--strings', type=open,
                            help='Read strings to be converted from this file')
        parser.add_argument('--single', type=str,
                            help='Single string to be converted')

    def _migrate(self, filename, strict=True):
        catalog = catalogs.make_current_catalog()
        org_matching.Migrater(catalog).run(filename)
        org_matching.backfill(catalog, strict=strict)
        LOG.info("Migration completed")

    def handle(self, filename, **options):
        catalog = catalogs.make_current_catalog()
        nos_orgs = catalog.Organisation.objects.all().count()
        if nos_orgs == 0:
            LOG.error("The initial ROR dump must be loaded before migrating")
        if options['migrate']:
            if options['check']:
                LOG.error("Only one of --migrate or --check is allowed")
            else:
                strict = not options['nonstrict']
                self._migrate(filename, strict=strict)
        elif options['check']:
            matcher = org_matching.TrialMatcher(catalog)
            if options['strings']:
                matcher.run(filename, options['strings'])
            elif options['single']:
                matcher.run(filename, [options['single']])
            else:
                ci_institutions = catalog.ChiefInvestigator.objects.all() \
                        .values_list('institution', flat=True)
                primary_institutions = catalog.Institution.objects.all() \
                        .values_list('name', flat=True)
                all_institutions = set(
                    itertools.chain(ci_institutions.iterator(),
                                    primary_institutions.iterator()))
                matcher.run(filename, sorted(all_institutions))
        else:
            LOG.error("One of --migrate or --check is required")
