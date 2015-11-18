import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from rcportal.rcallocation.models import AllocationRequest
from . import _common as common


_request_status_key = map(lambda c: '{}: {:<50}'.format(*c),
                          sorted(common.REQUEST_STATUS_CHOICES.items()))
REQUEST_STATUS_HELP = """Status of the allocation. Must be one of:
                         %s""" % ' '.join(_request_status_key)


class Command(BaseCommand):
    args = '<allocation_id>'
    help = 'Update an allocation.'
    option_list = BaseCommand.option_list + (
        make_option('--name',
                    action='store',
                    dest='tenant_name',
                    help="Alternative Tenant Name."),
        make_option('--uuid',
                    action='store',
                    dest='tenant_uuid',
                    help="The UUID of the tenant."),
        make_option('--email',
                    action='store',
                    dest='contact_email',
                    help="Email address of the tenant manager."),
        make_option('--status',
                    action='store',
                    dest='status',
                    choices=common.REQUEST_STATUS_CHOICES.keys(),
                    help=REQUEST_STATUS_HELP),
        )

    def print_help(self):
        super(Command, self).print_help(sys.argv[0], 'update')

    def handle(self, *args, **options):
        try:
            allocation_id = int(args[0])
        except:
            self.print_help()
            raise CommandError('Requires an allocation id as input.')

        kc = common.get_keystone_client()

        pk = allocation_id
        qs = AllocationRequest.objects.filter(
            Q(parent_request=pk) | Q(pk=pk)).order_by('-modified_time')
        allocation = qs[0]
        print "\nAllocation"
        print allocation.tenant_uuid, allocation.tenant_name, \
            allocation.project_name, '\n'
        most_recent = common.print_allocation_history(qs)

        # If the tenant uuid mapping doesn't exist then update it.
        allocation = AllocationRequest.objects.get(pk=pk)
        if options['tenant_uuid']:
            # Try and find Tenant
            kc.tenants.get(options['tenant_uuid'])
            allocation.tenant_uuid = options['tenant_uuid']
        if options['tenant_name']:
            allocation.tenant_name = options['tenant_name']
            # Try and find Tenant
            tenant = kc.tenants.get(allocation.tenant_uuid)
            kc.tenants.update(tenant.id, name=options['tenant_name'])
        if options['contact_email']:
            # Try and find account
            kc.users.find(name=options['contact_email'])
            allocation.contact_email = options['contact_email']
        if options['status']:
            allocation.status = options['status']
        if allocation.tenant_uuid:
            tenant = kc.tenants.get(allocation.tenant_uuid)
            expiry = most_recent.end_date.strftime(common.DATEFORMAT)
            kwargs = {'allocation_id': pk,
                      'expires': expiry}
            kc.tenants.update(tenant.id, **kwargs)
        allocation.save(provisioning=True)
        print "Allocation updated."
