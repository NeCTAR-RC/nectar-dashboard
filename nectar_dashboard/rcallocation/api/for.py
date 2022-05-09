# Copyright 2022 Australian Research Data Commons
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import response
from rest_framework import viewsets

from horizon.utils import memoized

from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import models


@memoized.memoized
def get_instances_resource_id():
    return models.Resource.objects.get_by_path('compute.instances').id


@memoized.memoized
def get_cores_resource_id():
    return models.Resource.objects.get_by_path('compute.cores').id


@memoized.memoized
def get_budget_resource_id():
    return models.Resource.objects.get_by_path('rating.budget').id


class FOR2008ViewSet(viewsets.GenericViewSet):

    @method_decorator(cache_page(86400))
    def list(self, request, *args, **kwargs):
        return response.Response(forcodes.FOR_CODES_2008)


class FOR2020ViewSet(viewsets.GenericViewSet):

    @method_decorator(cache_page(86400))
    def list(self, request, *args, **kwargs):
        return response.Response(forcodes.FOR_CODES_2020)


class FORAllViewSet(viewsets.GenericViewSet):

    @method_decorator(cache_page(86400))
    def list(self, request, *args, **kwargs):
        return response.Response(forcodes.FOR_CODES_ALL)


class AllocationTree2008ViewSet(viewsets.GenericViewSet):

    @method_decorator(cache_page(86400))
    def list(self, request, *args, **kwargs):
        tree = restructure_allocations_tree(forcodes.FOR_CODES_2008)
        return response.Response(tree)


class AllocationTree2020ViewSet(viewsets.GenericViewSet):

    @method_decorator(cache_page(86400))
    def list(self, request, *args, **kwargs):
        tree = restructure_allocations_tree(forcodes.FOR_CODES_2020)
        return response.Response(tree)


class AllocationTreeAllViewSet(viewsets.GenericViewSet):

    @method_decorator(cache_page(86400))
    def list(self, request, *args, **kwargs):
        tree = restructure_allocations_tree(forcodes.FOR_CODES_ALL)
        return response.Response(tree)


def partition_active_allocations(for_code_map):
    allocation_summaries = list()
    active_allocations = models.AllocationRequest.objects \
            .filter(status__in=[models.AllocationRequest.APPROVED,
                    models.AllocationRequest.UPDATE_PENDING]) \
            .filter(parent_request__isnull=True) \
            .prefetch_related(
                Prefetch('quotas',
                         queryset=models.QuotaGroup.objects.filter(
                             service_type__in=['compute', 'rating'],
                             zone='nectar')),
                Prefetch('quotas__quota_set', to_attr='quota_cache'))

    codes = for_code_map.keys()
    for active_allocation in active_allocations:
        code = active_allocation.field_of_research_1
        if code in codes:
            allocation_summaries.append(summary(active_allocation, code))
        code = active_allocation.field_of_research_2
        if code in codes:
            allocation_summaries.append(summary(active_allocation, code))
        code = active_allocation.field_of_research_3
        if code in codes:
            allocation_summaries.append(summary(active_allocation, code))
    return allocation_summaries


def organise_allocations_tree(for_code_map):
    allocations = partition_active_allocations(for_code_map)
    allocations_tree = dict()

    for allocation in allocations:
        allocation_code_2 = allocation['for_2']
        if allocation_code_2 not in allocations_tree:
            allocations_tree[allocation_code_2] = dict()
        branch_major = allocations_tree[allocation_code_2]
        allocation_code_4 = allocation['for_4']
        if allocation_code_4 not in branch_major:
            branch_major[allocation_code_4] = dict()
        branch_minor = branch_major[allocation_code_4]
        allocation_code_6 = allocation['for_6']
        if allocation_code_6 not in branch_minor:
            branch_minor[allocation_code_6] = list()
        twig = dict()
        twig['id'] = allocation['id']
        twig['projectDescription'] = allocation['project_description']
        twig['institution'] = allocation['institution']
        twig['instanceQuota'] = allocation['instance_quota']
        twig['coreQuota'] = allocation['core_quota']
        twig['budgetQuota'] = allocation['budget_quota']
        twig['national'] = allocation['national']
        branch_minor[allocation_code_6].append(twig)
    return allocations_tree


def create_allocation_tree_branch_node(name):
    return {'name': name, 'children': []}


def create_allocation_tree_leaf_node(allocation_summary):
    allocation_items = {
        'id': allocation_summary['id'],
        'name': allocation_summary['projectDescription'],
        'institution': allocation_summary['institution'],
        'instanceQuota': allocation_summary['instanceQuota'],
        'coreQuota': allocation_summary['coreQuota'],
        'budgetQuota': allocation_summary['budgetQuota'],
        'national': allocation_summary['national'],
    }
    return allocation_items


def restructure_allocations_tree(for_code_map):
    allocations_tree = organise_allocations_tree(for_code_map)
    restructured_tree = create_allocation_tree_branch_node('allocations')
    traverse_allocations_tree(allocations_tree, restructured_tree, 0)
    return restructured_tree


def traverse_allocations_tree(allocations_tree, node_parent, recursion_depth):
    MAX_RECURSION_DEPTH = 2
    for node_name in allocations_tree.keys():
        node_children = create_allocation_tree_branch_node(node_name)
        node_parent['children'].append(node_children)
        allocations_subtree = allocations_tree[node_name]
        if recursion_depth < MAX_RECURSION_DEPTH:
            traverse_allocations_tree(allocations_subtree, node_children,
                                      recursion_depth + 1)
        else:
            for allocation_summary in allocations_subtree:
                allocation_items = create_allocation_tree_leaf_node(
                    allocation_summary)
                node_children['children'].append(allocation_items)


def apply_for_code_to_summary(allocation_summary, code):
    allocation_summary['for_2'] = code[:2]
    allocation_summary['for_4'] = code[:4]
    allocation_summary['for_6'] = code[:6]


def apply_partitioned_quotas(allocation, allocation_summary, percentage):
    fraction = float(percentage) / 100.0
    instance_quota = 0
    core_quota = 0
    budget_quota = 0

    for group in allocation.quotas.all():
        for quota in group.quota_cache:
            if quota.resource_id == get_instances_resource_id():
                instance_quota = quota.quota
            elif quota.resource_id == get_cores_resource_id():
                core_quota = quota.quota
            elif quota.resource_id == get_budget_resource_id():
                budget_quota = quota.quota
    allocation_summary['instance_quota'] = instance_quota * fraction
    allocation_summary['core_quota'] = core_quota * fraction
    allocation_summary['budget_quota'] = budget_quota * fraction


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


def summary(allocation, code):
    allocation_summary = dict()
    allocation_summary['id'] = allocation.id
    allocation_summary['institution'] = institution_from_email(
        allocation.contact_email)
    allocation_summary['project_description'] = allocation.project_description
    allocation_summary['national'] = allocation.national
    apply_for_code_to_summary(allocation_summary, code)
    if code == allocation.field_of_research_1:
        apply_partitioned_quotas(
            allocation,
            allocation_summary,
            allocation.for_percentage_1)
    elif code == allocation.field_of_research_2:
        apply_partitioned_quotas(
            allocation,
            allocation_summary,
            allocation.for_percentage_2)
    elif code == allocation.field_of_research_3:
        apply_partitioned_quotas(
            allocation,
            allocation_summary,
            allocation.for_percentage_3)
    return allocation_summary
