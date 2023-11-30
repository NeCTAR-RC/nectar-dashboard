import logging

from django.core.management.base import BaseCommand

from nectar_dashboard.rcallocation.management import org_loading
from nectar_dashboard.rcallocation import models


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load or update the Organisations table from a ROR dump file'

    def add_arguments(self, parser):
        parser.add_argument('filename',
                            help="The ROR dump file pathname")
        parser.add_argument('--initial', action='store_true',
                            help='Expecteding to perform the initial ROR load')

    def handle(self, filename, **options):
        nos_orgs = models.Organisation.objects.all().count()
        loader = org_loading.Loader()
        if options['initial']:
            if nos_orgs > 0:
                LOG.error("The Organisation table is not empty")
            else:
                loader.load(filename, initial=True)
        else:
            loader.load(filename)
