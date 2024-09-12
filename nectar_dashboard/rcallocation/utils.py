# Copyright 2022 Australian Research Data Commons
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from copy import deepcopy
import logging
import os
import urllib

from django.conf import settings
from django.db.models import F
from django.db.models import Func
from django.db.models import Value
from horizon.utils import memoized

from nectar_dashboard.rcallocation import models

LOG = logging.getLogger(__name__)


def user_is_allocation_admin(user):
    return user.has_perm('openstack.roles.allocationadmin')


def copy_allocation(allocation):
    """Create and save a history copy of 'allocation', and its component
    objects.  The history object will have a different id, and its
    'parent_request' will point to original allocation.  All other
    fields (including the 'modified_time') will be the same, and
    the copied component object graphs will be isomorphic with the
    those of the original.

    The result is the history copy for the allocation record.

    Note: this should be called when 'allocation' is a clean copy.
    The history record is going to be a clone of what is currently in
    the database.  (We don't check this precondition ... so beware.)
    """

    manager = models.AllocationRequest.objects
    old_object = manager.get(id=allocation.id)
    old_object.parent_request = allocation
    quota_groups = deepcopy(old_object.quotas.all())
    investigators = deepcopy(old_object.investigators.all())
    publications = deepcopy(old_object.publications.all())
    grants = deepcopy(old_object.grants.all())
    usage_types = deepcopy(old_object.usage_types.all())

    # Don't deep copy these.  They are shared by all allocations
    supported_organisations = old_object.supported_organisations.all()

    old_object.id = None
    save_allocation_without_updating_timestamps(old_object)

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

    for pub in publications:
        pub.id = None
        pub.allocation = old_object
        pub.save()

    for grant in grants:
        grant.id = None
        grant.allocation = old_object
        grant.save()

    for usage_type in usage_types:
        old_object.usage_types.add(usage_type)

    for org in supported_organisations:
        old_object.supported_organisations.add(org)

    return old_object


def save_allocation_without_updating_timestamps(allocation):
    """Saves AllocationRequest without auto-updating the timestamps.
    Note that if you do this when the 'submit_date' is None, you
    may get DB constraint violation, because there is a not-null
    constraint on the field.
    """

    manager = models.AllocationRequest.objects
    saved_modified_time = allocation.modified_time
    saved_submit_date = allocation.submit_date

    # Save does the 'auto_*' updates
    allocation.save()

    # Reverse the effect of the 'auto_*' updates in the DB
    manager.filter(id=allocation.id).update(modified_time=saved_modified_time)
    manager.filter(id=allocation.id).update(submit_date=saved_submit_date)

    # ... and reset the values in 'self'
    allocation.modified_time = saved_modified_time
    allocation.submit_date = saved_submit_date


# The following are the domain "normalization" methods written
# for the "/fortree" API.  We should consider replacing them with
# code based on Andy Botting's "domain-categories.yaml" file and
# the associate "categorizer.py" code.


def is_project_name_available(project_name, allocation=None):
    manager = models.AllocationRequest.objects
    if allocation:
        manager = manager.exclude(id=allocation.id).exclude(
            parent_request_id=allocation.id)
    normalized_name = manager.filter().annotate(
      normalized_name=Func(
        F('project_name'), Value('_'), Value('-'), function='replace',
      )
    ).annotate(
      project_names=Func(
        F('normalized_name'), function='LOWER',
      )
    )
    project_names = normalized_name.all().values_list(
        'project_names', flat=True)
    project_name = project_name.lower().replace('_', '-')
    return project_name not in project_names


def strip_email_sub_domains(domain):
    prefix = domain.split('.', 1)[0]
    if prefix in ('my', 'ems', 'exchange', 'groupwise',
                  'student', 'students', 'studentmail'):
        _, _, domain = domain.partition('.')
        if domain == 'griffithuni.edu.au':
            return 'griffith.edu.au'
        if domain == 'waimr.uwa.edu.au':
            return 'uwa.edu.au'
        if domain == 'uni.sydney.edu.au':
            return 'sydney.edu.au'
        if domain == 'usyd.edu.au':
            return 'sydney.edu.au'
        if domain == 'myune.edu.au':
            return 'une.edu.au'
        if domain == 'aucklanduni.ac.nz':
            return 'auckland.ac.nz'
        if domain == 'data61.csiro.au':
            return 'csiro.au'
    return domain


def extract_email_domain(email_address):
    _, _, domain = email_address.partition('@')
    return domain


def institution_from_email(contact_email):
    email_domain = extract_email_domain(contact_email)
    domain = strip_email_sub_domains(email_domain)
    return domain


@memoized.memoized
def get_member_map():
    res = {}
    for site_name, domains in settings.SITE_MEMBERS_MAPPING.items():
        try:
            site = models.Site.objects.get(name=site_name)
            for domain in domains:
                if domain in res:
                    res[domain].append(site)
                else:
                    res[domain] = [site]
        except models.Site.DoesNotExist:
            LOG.error(f"Unknown site {site_name} in SITE_MEMBERS_MAP")
    return res


def sites_from_email(contact_email):
    domain = institution_from_email(contact_email)
    return get_member_map().get(domain, [])


def open_config_file(uri):
    """Open a config file.  If the uri is relative, treat it as a local
    pathname.  If it is a URL, download and cache the file locally in
    the current directory with a filename given by the URL's last path
    component.  Returns an opened file which the caller should close.
    """

    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != "":
        filename = parsed.path.split("/")[-1]
        if not os.path.exists(filename):
            LOG.info(f"Downloading config file from {uri}")
            urllib.request.urlretrieve(uri, filename)
        else:
            LOG.info(f"Using cached config file: {filename}")
    else:
        filename = uri
        LOG.info(f"Using builtin config file: {filename}")

    return open(filename, mode='r')
