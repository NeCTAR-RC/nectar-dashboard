import sys
from optparse import make_option

from django.core.management.base import BaseCommand

from . import create


class Command(create.Command):
    args = ''
    help = 'Provision allocations.'
    option_list = BaseCommand.option_list + (
        make_option('--noop',
                    action='store_true',
                    dest='noop',
                    default=False,
                    help="Don't perform any changes, instead "
                    "just print what would happen."),
        make_option('--unattended',
                    action='store_true',
                    dest='unattended',
                    default=False,
                    help="Run without prompts. Skip allocations that need "
                         "manual intervention."),
    )

    def print_help(self):
        super(Command, self).print_help(sys.argv[0], 'provision')

    def handle(self, *args, **options):
        self.init_clients()
        noop = options.get('noop', False)
        unattended = options.get('unattended', False)

        from . import _rt as rt
        rtclient = rt.get_rt_client()
        requests = rt.get_allocation_requests(rtclient)
        for allocation_id, ticket_id in requests:
            print allocation_id, ticket_id
            email = None
            try:
                email = self.provision_allocation(allocation_id, noop=noop,
                                                  unattended=unattended)
            except Exception, e:
                print 'Error provisioning allocation:'
                print str(e)
                message = 'Error provisioning allocation:\n %s' % str(e)
                rt.comment_ticket(rtclient, ticket_id, message)
                rt.open_ticket(rtclient, ticket_id)
            if not noop and email is not None:
                rt.take_and_resolve_ticket(rtclient, ticket_id, email)
