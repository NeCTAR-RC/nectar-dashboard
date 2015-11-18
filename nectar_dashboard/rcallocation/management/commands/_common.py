import os
import sys
import time
from collections import defaultdict

import prettytable
from keystoneclient.v2_0 import client as ks_client
from keystoneclient.exceptions import AuthorizationFailure
from keystoneclient.openstack.common.apiclient.exceptions \
    import Conflict as ConflictException
from novaclient import client as nova_client
from cinderclient.v1 import client as cinder_client
from swiftclient import client as swift_client


SWIFT_QUOTA_KEY = 'x-account-meta-quota-bytes'

DATEFORMAT = "%Y-%m-%d"

REQUEST_STATUS_CHOICES = dict([
    # Request created but nothing else
    # User can: Submit
    ('N', 'New'),

    # Request has been emailed
    # Admin can: Approve, Reject, Edit
    # User can: Edit
    ('E', 'Submitted'),

    # Admin has approved the request
    # Admin can: Provision
    # User can: Amend, Extend
    ('A', 'Approved'),

    # Admin has rejected the request
    # User can: Edit, Submit
    ('R', 'Declined'),

    # User has requested an extension
    # Admin can: Approve, Reject, Edit
    # User can: Edit
    ('X', 'Update/extension requested'),

    # Admin has rejected an extension
    # User can: Edit, Extend
    ('J', 'Update/extension declined'),

    # Admin has provisioned an approved request
    # User can: Amend, Extend
    ('P', 'Provisioned'),

    # Requests in above status can be viewed by both user
    # and admin at all times.

    # Not visible to users
    ('L', 'Legacy submission'),

    # Avoid sending emails for legacy approvals/rejections.
    # Set to A/R during model save.
    ('M', 'Legacy approved'),
    ('O', 'Legacy rejected')])


def add_tenant(kc, name, description, manager_email, allocation_id, expiry):

    try:
        tenant_manager = kc.users.find(name=manager_email)
    except:
        print "Couldn't find a unique user with that email"
        return sys.exit(1)

    try:
        tenant_manager_role = kc.roles.find(name='TenantManager')
        member_role = kc.roles.find(name='Member')
    except:
        print "Couldn't find roles"
        return sys.exit(1)

    # Create tenant
    tenant = kc.tenants.create(name, description)

    # Link tenant to allocation
    kwargs = {'allocation_id': allocation_id, 'expires': expiry}
    kc.tenants.update(tenant.id, **kwargs)

    # Add roles to tenant manager
    kc.tenants.add_user(tenant, tenant_manager, tenant_manager_role)
    kc.tenants.add_user(tenant, tenant_manager, member_role)

    return tenant


def update_tenant(kc, tenant, allocation_id, expiry):
    # Link tenant to allocation
    tenantd = tenant.to_dict()
    kwargs = {}
    if allocation_id:
        kwargs['allocation_id'] = allocation_id
    else:
        if 'allocation_id' not in tenantd:
            print "ERROR: no tenant has no allocation_id."
            return sys.exit(1)
    kwargs['expires'] = expiry
    tenant = kc.tenants.update(tenant.id, **kwargs)

    return tenant


def get_cinder_quota(cc, tenant):
    quota = cc.quotas.get(tenant_id=tenant.id)
    return quota


def add_cinder_quota(cc, tenant, type, gigabytes, volumes):
    if type == 'nectar':
        type = ''
    else:
        type = '_' + type

    kwargs = {}
    if gigabytes is not None:
        kwargs['gigabytes' + type] = gigabytes
    if volumes is not None:
        # volumes and snapshots are the same as we don't care
        kwargs['volumes' + type] = volumes
        kwargs['snapshots' + type] = volumes
    return cc.quotas.update(tenant_id=tenant.id, **kwargs)


def get_nova_quota(nc, tenant):
    quota = nc.quotas.get(tenant_id=tenant.id)
    return quota


def add_nova_quota(nc, tenant, cores, instances, ram):

    kwargs = {}
    if cores:
        kwargs['cores'] = cores
    if ram:
        kwargs['ram'] = ram
    if instances:
        kwargs['instances'] = instances

    quota = nc.quotas.update(tenant_id=tenant.id, **kwargs)
    return quota


def get_swift_tenant_connection(sc, tenant_id):
    url, token = sc.get_auth()
    base_url = url.split('_')[0] + '_'
    return base_url + tenant_id, token


def get_swift_quota(sc, tenant):
    tenant_url, token = get_swift_tenant_connection(sc,
                                                    tenant.id)
    swift_account = swift_client.head_account(url=tenant_url,
                                              token=token)
    return int(swift_account.get(SWIFT_QUOTA_KEY, -1)) / 1024 / 1024 / 1024


def add_swift_quota(sc, tenant, gigabytes):
    tenant_url, token = get_swift_tenant_connection(sc,
                                                    tenant.id)
    quota_bytes = int(gigabytes) * 1024 * 1024 * 1024
    attempt = 1
    max_attempts = 10
    while attempt <= max_attempts:
        try:
            swift_client.post_account(url=tenant_url,
                                      token=token,
                                      headers={SWIFT_QUOTA_KEY: quota_bytes})
            return
        except swift_client.ClientException as e:
            print e
            print "Failed to set swift quota, retying, attempt %s" % attempt
            time.sleep(attempt * 2)
            attempt += 1
    print "Failed to set swift quota for tenant %s" % tenant.id


def get_keystone_client():

    auth_username = os.environ.get('OS_USERNAME')
    auth_password = os.environ.get('OS_PASSWORD')
    auth_tenant = os.environ.get('OS_TENANT_NAME')
    auth_url = os.environ.get('OS_AUTH_URL')

    try:
        kc = ks_client.Client(username=auth_username,
                              password=auth_password,
                              tenant_name=auth_tenant,
                              auth_url=auth_url)
    except AuthorizationFailure as e:
        print e
        print 'Authorization failed, have you sourced your openrc?'
        sys.exit(1)

    return kc


def get_nova_client():

    auth_username = os.environ.get('OS_USERNAME')
    auth_password = os.environ.get('OS_PASSWORD')
    auth_tenant = os.environ.get('OS_TENANT_NAME')
    auth_url = os.environ.get('OS_AUTH_URL')

    nc = nova_client.Client(2,
                            username=auth_username,
                            api_key=auth_password,
                            project_id=auth_tenant,
                            auth_url=auth_url,
                            service_type='compute')
    return nc


def get_cinder_client():

    auth_username = os.environ.get('OS_USERNAME')
    auth_password = os.environ.get('OS_PASSWORD')
    auth_tenant = os.environ.get('OS_TENANT_NAME')
    auth_url = os.environ.get('OS_AUTH_URL')

    cc = cinder_client.Client(username=auth_username,
                              api_key=auth_password,
                              project_id=auth_tenant,
                              auth_url=auth_url)
    return cc


def get_swift_client():

    auth_username = os.environ.get('OS_USERNAME')
    auth_password = os.environ.get('OS_PASSWORD')
    auth_tenant = os.environ.get('OS_TENANT_NAME')
    auth_url = os.environ.get('OS_AUTH_URL')

    sc = swift_client.Connection(authurl=auth_url,
                                 user=auth_username,
                                 key=auth_password,
                                 tenant_name=auth_tenant,
                                 auth_version=2)

    return sc


def get_allocation_quotas(allocation):
    """Return a simple sum of an allocations storage types."""
    storage = defaultdict(int)
    for quota in allocation.quotas.all():
        storage[(quota.resource, quota.zone)] += quota.requested_quota
    return storage


def get_allocation_quotas_sum(allocation):
    """Return a simple sum of an allocations storage types."""
    storage = {'volume': 0, 'object': 0}
    for quota in allocation.quotas.all():
        want = quota.requested_quota
        storage[quota.resource] += want
    return storage


def get_allocation_quotas_deltas(allocation):
    """Return the change of an allocations of the storage types."""
    storage = {'volume': 0, 'object': 0}
    for quota in allocation.quotas.all():
        want = quota.requested_quota
        have = quota.quota
        storage[quota.resource] += (want - have)
    return storage


def print_allocation_history(allocations):
    pt = prettytable.PrettyTable(['Modified', 'Status', 'Name',
                                  'Instances', 'Cores',
                                  'Volume',
                                  'Object',
                                  'Expiry'],
                                 caching=False)
    most_recent = None
    for allocation in allocations:
        if not most_recent and allocation.status == 'A':
            most_recent = allocation
        if allocation.status == 'X':
            storage = get_allocation_quotas_deltas(allocation)
            instances = allocation.instances - allocation.instance_quota
            cores = allocation.cores - allocation.core_quota
            pt.add_row([allocation.modified_time,
                        REQUEST_STATUS_CHOICES[allocation.status],
                        allocation.project_name,
                        "%+d" % instances,
                        "%+d" % cores,
                        "%+d" % storage['volume'],
                        "%+d" % storage['object'],
                        allocation.end_date.strftime(DATEFORMAT)])
        else:
            storage = get_allocation_quotas_sum(allocation)
            pt.add_row([allocation.modified_time,
                        REQUEST_STATUS_CHOICES[allocation.status],
                        allocation.project_name,
                        allocation.instance_quota,
                        allocation.core_quota,
                        storage['volume'],
                        storage['object'],
                        allocation.end_date.strftime(DATEFORMAT)])
    print str(pt)
    return most_recent


def unlock_all_instances(project_id):
    nc = get_nova_client()
    opts = {"all_tenants": True, 'tenant_id': project_id}
    instances = nc.servers.list(search_opts=opts)
    for i in instances:
        i.unlock()


def convert_trial_project(username, new_project_name, new_project_description):
    client = get_keystone_client()

    member_role_id = client.roles.find(name='Member').id
    manager_role_id = client.roles.find(name='TenantManager').id
    user = client.users.find(name=username)
    old_trial_project_id = user.tenantId
    allocation_project = None
    try:
        test_name = client.tenants.find(name=new_project_name)
    except:
        test_name = None
    if test_name:
        print "Project already created"
        allocation_project = client.tenants.find(name=new_project_name)
        trial_project = client.tenants.get(user.tenantId)

    if not allocation_project:

        # Get name/desc of existing trial project.
        old_trial_project = client.tenants.get(old_trial_project_id)
        if not old_trial_project.name.startswith('pt-'):
            print "User's default project is not a pt- project! Aborting."
            return

        # Create new trial project.
        trial_project = client.tenants.create(old_trial_project.name + '_copy',
                                              old_trial_project.description)
        # Rename existing trial project to new project name/desc.
        # Reset status in case their pt- is pending suspension.
        allocation_project = client.tenants.update(
            old_trial_project_id,
            tenant_name=new_project_name,
            description=new_project_description,
            status='')
        # Rename new trial project to match old name.
        client.tenants.update(trial_project.id,
                              tenant_name=old_trial_project.name)

    try:
        # Add user to new project
        trial_project.add_user(user.id, member_role_id)
    except ConflictException:
        pass
    try:
        # Add TenantManager role on allocation project.
        client.roles.add_user_role(user.id, manager_role_id,
                                   allocation_project.id)
    except ConflictException:
        pass

    # This call removes the user's role from the *old* project.
    client.users.update(user.id, tenantId=trial_project.id)

    try:
        # Re-add that role.
        client.roles.add_user_role(user.id, member_role_id,
                                   allocation_project.id)
    except ConflictException:
        pass

    unlock_all_instances(allocation_project.id)

    return allocation_project
