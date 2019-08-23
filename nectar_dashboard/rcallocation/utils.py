from nectar_dashboard.rcallocation import models


def user_is_allocation_admin(user):
    return user.has_perm('openstack.roles.allocationadmin')


def copy_allocation(allocation):
    """Create and save a history copy of 'allocation', and its component
    objects.  The history object will have a different id, and its
    'parent_request' will point to original allocation.  All other
    fields (including the 'modified_time') will be the same, and
    the copied component object graphs will be isomorphic with the
    those of the original.
    """

    manager = models.AllocationRequest.objects
    old_object = manager.get(id=allocation.id)
    old_object.parent_request = allocation
    quota_groups = old_object.quotas.all()
    investigators = old_object.investigators.all()
    institutions = old_object.institutions.all()
    publications = old_object.publications.all()
    grants = old_object.grants.all()
    modified_time = old_object.modified_time

    old_object.id = None
    old_object.save()
    # Preserve the original modification timestamp on the old object.
    # (This reverses the "damage" of the 'auto_now' attribute.)
    manager.filter(id=old_object.id).update(modified_time=modified_time)

    for quota_group in quota_groups:
        old_quota_group_id = quota_group.id
        quota_group.id = None
        quota_group.allocation = old_object
        quota_group.save()
        old_quota_group = models.QuotaGroup.objects.get(id=old_quota_group_id)
        for quota in old_quota_group.quota_set.all():
            quota.id = None
            quota.group = quota_group
            quota.save()

    for inv in investigators:
        inv.id = None
        inv.allocation = old_object
        inv.save()

    for inst in institutions:
        inst.id = None
        inst.allocation = old_object
        inst.save()

    for pub in publications:
        pub.id = None
        pub.allocation = old_object
        pub.save()

    for grant in grants:
        grant.id = None
        grant.allocation = old_object
        grant.save()

    return old_object.id
