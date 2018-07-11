from django.conf import settings

from openstack_auth import user


def get_user(id='123', username='bob', tenant_name='foo', roles=['member']):
    roles = [{'name': role} for role in roles]
    return user.User(id=id,
                     token='fake',
                     user=username,
                     domain_id='default',
                     user_domain_name='Default',
                     tenant_id=tenant_name,
                     tenant_name=tenant_name,
                     service_catalog={},
                     roles=roles,
                     enabled=True,
                     authorized_tenants=[tenant_name,],
                     endpoint=settings.OPENSTACK_KEYSTONE_URL)

