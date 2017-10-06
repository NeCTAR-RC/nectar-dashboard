
def user_is_allocation_admin(user):
    return user.has_perm('openstack.roles.allocationadmin')
