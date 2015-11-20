import sys
from optparse import make_option
import textwrap

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.template.loader import render_to_string

from nectar_dashboard.rcallocation.models import AllocationRequest
from . import _common as common


class Command(BaseCommand):
    args = '<allocation_id>'
    help = 'Create an allocation.'
    option_list = BaseCommand.option_list + (
        make_option('--noop',
                    action='store_true',
                    dest='noop',
                    default=False,
                    help="Don't perform any changes, instead "
                    "just print what would happen."),
    )

    def print_help(self):
        super(Command, self).print_help(sys.argv[0], 'create')

    def parse_cquota(self, cquota):
        zones = {}
        if not cquota:
            return {}
        for resource, quota in sorted([(key, value)
                                       for key, value in cquota._info.items()
                                       if key.split('_', 1)[0]
                                       in ['volumes',
                                           'snapshots',
                                           'gigabytes']]):
            if quota == -1:
                continue
            type = resource.split('_', 1)
            if len(type) > 1:
                resource, zone = type
            else:
                resource = type[0]
                zone = 'nectar'
            if zone not in zones:
                zones[zone] = {resource: quota}
            else:
                zones[zone][resource] = quota
        return zones

    def print_quota(self, title, nquota, cquota, squota):
        quota_string = self. pretty_quota(title, nquota, cquota, squota)
        for line in quota_string:
            print line

    def pretty_quota(self, title, nquota, cquota, squota, include_zeros=True):
        quota_string = ["%s:" % title]
        quota_string.append('  Instances: %s' % nquota.instances)
        quota_string.append('  Cores: %s' % nquota.cores)
        quota_string.append('  Ram: %s' % nquota.ram)
        for zone, resources in self.parse_cquota(cquota).items():
            for resource, quota in resources.items():
                if include_zeros or quota > 0:
                    quota_string.append('  %s (%s): %s' % (resource,
                                                           zone, quota))
        if include_zeros or squota > 0:
            quota_string.append('  Object Store Gigabytes: %s' % squota)
        return quota_string

    def init_clients(self):
        self.kc = common.get_keystone_client()
        self.nc = common.get_nova_client()
        self.cc = common.get_cinder_client()
        self.sc = common.get_swift_client()

    def handle(self, *args, **options):
        try:
            allocation_id = int(args[0])
        except:
            self.print_help()
            raise CommandError('Requires an allocation id as input.')

        self.init_clients()
        noop = options.get('noop', False)

        email = self.provision_allocation(allocation_id, noop)

        if not noop and email is not None:
            from . import _rt as rt
            rtclient = rt.get_rt_client()
            rt.resolve_allocation_ticket(rtclient, allocation_id, email)

    def provision_allocation(self, allocation_id, noop=True, unattended=False):
        pk = int(allocation_id)
        qs = AllocationRequest.objects.filter(
            Q(parent_request=pk) | Q(pk=pk)).order_by('-modified_time')
        allocation = qs[0]
        print "\nAllocation"
        print allocation.tenant_uuid, allocation.tenant_name, \
            allocation.project_name, '\n'
        most_recent = common.print_allocation_history(qs)
        expiry = most_recent.end_date.strftime(common.DATEFORMAT)

        tenant = None
        tenant_uuid = None
        if not most_recent:
            print "No approved allocations."
            sys.exit(0)
        if most_recent.tenant_uuid:
            tenant = self.kc.tenants.get(most_recent.tenant_uuid)
            tenant_uuid = tenant.id

        squota = None
        if tenant:
            nquota = common.get_nova_quota(self.nc, tenant)
            cquota = common.get_cinder_quota(self.cc, tenant)
            squota = common.get_swift_quota(self.sc, tenant)
            self.print_quota("Current Quota", nquota, cquota, squota)
        else:
            cquota = {}
        storage = common.get_allocation_quotas(most_recent)
        if tenant and nquota.ram % 4096 == 0:
            ram = most_recent.core_quota * 4096
            # Don't reduce the ram if the tenant has already got more
            # ram.  Who knows why they have more ram, but don't reduce
            # it if the core count isn't smaller
            if most_recent.core_quota >= nquota.cores and nquota.ram > ram:
                ram = nquota.ram
        elif not tenant:
            ram = most_recent.core_quota * 4096
        if tenant:
            if nquota.instances > most_recent.instance_quota:
                instances = nquota.instances
            elif nquota.instances == most_recent.core_quota:
                instances = most_recent.core_quota
            else:
                instances = most_recent.instance_quota
            if squota is not None and squota != -1:
                objects = storage[('object', 'nectar')]
            else:
                objects = 0

        else:
            instances = most_recent.instance_quota
            objects = storage[('object', 'nectar')]
        cores = most_recent.core_quota

        # Some requests are very optimistic about whether 16 core VMs
        # will be available. Make sure there are at least enough instances
        # to exhaust the cores quota with 4-core VMs.
        if instances < (cores / 4):
            instances = cores / 4

        print "\nNew Quota:"
        print '  Instances', instances
        print '  Cores', cores
        print '  Ram', ram

        print '  Object Store (nectar)', objects, 'GB'

        for resource, zone in storage:
            if resource != 'volume':
                continue
            print '  Volumes (%s)' % zone, storage[(resource, zone)], 'GB'

        print ''
        print 'project_name', allocation.project_name
        print 'manager', allocation.contact_email
        print 'tenant_name', allocation.tenant_name
        print 'expiry', expiry
        print ''

        if most_recent.tenant_name:
            name = most_recent.tenant_name
        else:
            name = most_recent.project_name.strip() \
                                           .replace(" ", "_") \
                                           .replace(".", "_") \
                                           .replace("__", "_")
            if len(name) > 30:
                if unattended:
                    print "Name too long and being run unattended. Skipping."
                    return
                print 'Name is too long: %s' % name
                name = raw_input("Choose a better project name: ")

        if not noop and not unattended:
            var = raw_input("Would you like to update tenant %s?: " %
                            name)
            if var != 'yes':
                print "Aborted."
                sys.exit(1)
        allocation_id = most_recent.id
        if noop:
            print 'NOOP: Not performing actions.'
        if not most_recent.tenant_uuid:
            created = True
            if noop:
                print "# add_tenant", repr((name,
                                            allocation.project_name,
                                            most_recent.contact_email,
                                            allocation_id, expiry))
                # Dummy tenant so other bits work.  NeCTAR-Devs
                tenant = self.kc.tenants.get(
                    '2f6f7e75fc0f453d9c127b490b02e9e3')
            else:
                if most_recent.convert_trial_project:
                    tenant = common.convert_trial_project(
                        most_recent.contact_email,
                        name,
                        most_recent.project_name)
                    if tenant is None:
                        return
                else:
                    tenant = common.add_tenant(self.kc,
                                               name,
                                               most_recent.project_name,
                                               most_recent.contact_email,
                                               allocation_id, expiry)
                tenant_uuid = tenant.id
                allocation = AllocationRequest.objects.get(pk=pk)
                allocation.tenant_uuid = tenant.id
                allocation.tenant_name = tenant.name
                allocation.save(provisioning=True)
        else:
            created = False
            if noop:
                print "# update_tenant", repr((tenant_uuid, allocation_id,
                                               expiry))
            else:
                tenant = common.update_tenant(self.kc, tenant, allocation_id,
                                              expiry)
        selected_zones = set([])
        if noop:
            print "# add_nova_quota", repr((tenant_uuid, cores, instances,
                                            ram))
            for resource, zone in storage:
                if resource != 'volume':
                    continue
                volumes = storage[(resource, zone)]
                print "# add_cinder_quota", repr((tenant_uuid, zone,
                                                  volumes, volumes))
            print "# add_swift_quota", repr((tenant_uuid, objects))
        else:
            common.add_nova_quota(self.nc, tenant, cores, instances, ram)
            requesting_nectar_quota = False
            for resource, zone in storage:
                if resource != 'volume':
                    continue
                if zone == 'nectar':
                    requesting_nectar_quota = True
                else:
                    selected_zones.add(zone)
                volumes = storage[(resource, zone)]
                common.add_cinder_quota(self.cc, tenant, zone,
                                        volumes, volumes)

            all_zones = set([x[0] for x in
                             settings.ALLOCATION_VOLUME_AZ_CHOICES])
            if not requesting_nectar_quota:
                # If moving to zone quota set global quota to unlimited.
                # Quota is now enforced at the zone (type) level.
                common.add_cinder_quota(self.cc, tenant, 'nectar', -1, -1)
                zero_zones = all_zones - selected_zones
                for zone in zero_zones:
                    common.add_cinder_quota(self.cc, tenant, zone, 0, 0)
            if objects > -1:
                common.add_swift_quota(self.sc, tenant, objects)

        print "\n\n#######################################\n"
        print "Please cut and paste this into the RT response\n"
        print "#######################################\n\n"
        quota = self.pretty_quota("New Quota",
                                  common.get_nova_quota(self.nc, tenant),
                                  common.get_cinder_quota(self.cc, tenant),
                                  common.get_swift_quota(self.sc, tenant),
                                  include_zeros=False)
        if created is True:
            context = self.create_context(allocation, tenant, expiry, quota)
            email = self.get_create_email(context)
        else:
            old_quotas = self.pretty_quota("Initial Quota", nquota,
                                           cquota, squota, include_zeros=False)
            context = self.create_context(allocation, tenant, expiry,
                                          quota, old_quotas)
            email = self.get_update_email(context)

        print email

        if noop:
            return

        if created is True:
            allocation = AllocationRequest.objects.get(pk=pk)
            allocation.tenant_uuid = tenant.id
            allocation.tenant_name = tenant.name
            allocation.instance_quota = instances
            allocation.save(provisioning=True)

        return email

    def get_create_email(self, context):
        return render_to_string('rcallocation/commands/create_email.txt',
                                context)

    def get_update_email(self, context):
        return render_to_string('rcallocation/commands/update_email.txt',
                                context)

    def create_context(self, allocation, tenant, expiry, quotas,
                       old_quotas=None):
        approver_comment = None
        if allocation.status_explanation:
            approver_comment = '\n'.join(
                [textwrap.fill(line) for line in
                 allocation.status_explanation.split('\r\n')])
        context = {
            'tenant_uuid': tenant.id,
            'allocation_id': allocation.id,
            'approver_comment': approver_comment,
            'tenant': tenant,
            'expiry': expiry,
            'quotas': quotas,
            'old_quotas': old_quotas,
        }
        return context
