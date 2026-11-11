# Copyright 2021 Australian Research Data Commons
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

from unittest import mock

from django.contrib.auth import models as auth_models

from nectar_dashboard.rcallocation import checkers
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


def build_quota(service, resource, value, zone='nectar'):
    # Build a form field for a specific quota
    return {f'quota-{service}.{resource}__{zone}': value}


class FakeForm:
    def __init__(self, values):
        self.cleaned_data = values


DUMMY_FORM = FakeForm({})


def build_checker(
    form=DUMMY_FORM, approver=None, allocation=None, approve_action=False
):
    if approver is None:
        return checkers.QuotaSanityChecker(
            form=form, allocation=allocation, approve_action=approve_action
        )
    else:
        user = auth_models.User(username=approver)
        return checkers.QuotaSanityChecker(
            form=form,
            allocation=allocation,
            user=user,
            approving=True,
            approve_action=approve_action,
        )


class QuotaSanityCheckerTest(base.BaseTestCase):
    def test_empty_checker(self):
        checker = checkers.QuotaSanityChecker()
        self.assertIsNone(checker.form)

    def test_nonempty_checker(self):
        checker = build_checker()
        self.assertEqual(DUMMY_FORM, checker.form)

    # Testing the 'add_quotas' method would entail constructing
    # a quota formset populated with semi-sensible quotas.  Hard.

    def test_do_checks(self):
        checker = build_checker()
        check1 = mock.Mock(return_value='foo')
        check2 = mock.Mock(return_value=['bar', 'hello'])
        checker.CHECKS = [check1, check2]
        res = checker.do_checks()
        self.assertEqual(['foo', 'bar', 'hello'], res)


class QuotaSanityChecksTest(base.BaseTestCase):
    def test_cinder_checks(self):
        data = build_quota('volume', 'gigabytes', 10, 'QRIScloud')

        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertIsNone(checkers.cinder_local_check(checker))

        data.update({'associated_site': None})
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertIsNone(checkers.cinder_local_check(checker))

        data.update({'associated_site': common.get_site('qcif')})
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertIsNone(checkers.cinder_local_check(checker))

        data.update({'associated_site': common.get_site('monash')})
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertEqual(
            checkers.CINDER_NOT_LOCAL, checkers.cinder_local_check(checker)[0]
        )
        self.assertEqual(
            'monash approved local allocation requests '
            'volume storage in QRIScloud',
            checkers.cinder_local_check(checker)[1],
        )

        data.update({'national': True})
        checker = build_checker(form=form, approver="test_user")
        self.assertEqual(
            checkers.CINDER_NOT_LOCAL, checkers.cinder_local_check(checker)[0]
        )
        self.assertEqual(
            'monash approved national allocation requests '
            'volume storage in QRIScloud',
            checkers.cinder_local_check(checker)[1],
        )

        data = build_quota('volume', 'gigabytes', 10, 'monash-03')
        data.update({'associated_site': common.get_site('monash')})
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertIsNone(checkers.cinder_local_check(checker))

    def test_manila_checks(self):
        data = build_quota('share', 'shares', 10, 'QRIScloud')
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertIsNone(checkers.manila_local_check(checker))

        data.update({'associated_site': None})
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertIsNone(checkers.manila_local_check(checker))

        data.update({'associated_site': common.get_site('uom')})
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertEqual(
            checkers.MANILA_NOT_LOCAL, checkers.manila_local_check(checker)[0]
        )
        self.assertEqual(
            'uom approved local allocation requests shares in QRIScloud',
            checkers.manila_local_check(checker)[1],
        )

        data.update({'national': True})
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertEqual(
            checkers.MANILA_NOT_LOCAL, checkers.manila_local_check(checker)[0]
        )
        self.assertEqual(
            'uom approved national allocation requests shares in QRIScloud',
            checkers.manila_local_check(checker)[1],
        )

    def test_flavor_check(self):
        data = build_quota('compute', 'flavor:hugeram-v3', 0)
        form = FakeForm(data)
        checker = build_checker(form=form)
        self.assertIsNone(checkers.flavor_check(checker))

        data = build_quota('compute', 'flavor:hugeram-v3', 1)
        form = FakeForm(data)
        checker = build_checker(form=form)
        self.assertEqual(
            checkers.FLAVORS_NOT_JUSTIFIED, checkers.flavor_check(checker)[0]
        )

        data.update({'usage_patterns': 'Need lots of RAM ... because reasons'})
        form = FakeForm(data)
        checker = build_checker(form=form)
        self.assertIsNone(checkers.flavor_check(checker))


MODELS_LOG = 'nectar_dashboard.rcallocation.models.LOG'


class QuotaSanityApproverChecksTest(base.BaseTestCase):
    def test_approver_authority_checks(self):
        data = build_quota('volume', 'gigabytes', 1, 'QRIScloud')
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user")
        self.assertEqual([], checkers.approver_checks(checker))

    def test_not_approver(self):
        data = build_quota('volume', 'gigabytes', 1, 'QRIScloud')
        form = FakeForm(data)
        checker = build_checker(form=form, approver="not_a_user")
        with mock.patch(MODELS_LOG) as mock_log:
            self.assertEqual(
                checkers.APPROVER_PROBLEM, checkers.approver_checks(checker)[0]
            )
            mock_log.warning.assert_called_once()

    def test_no_approver_sites(self):
        data = build_quota('volume', 'gigabytes', 1, 'QRIScloud')
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user3")
        with mock.patch(MODELS_LOG) as mock_log:
            self.assertEqual(
                checkers.APPROVER_PROBLEM, checkers.approver_checks(checker)[0]
            )
            mock_log.warning.assert_called_once()

    def test_approver_not_authorized(self):
        data = build_quota('volume', 'gigabytes', 1, 'QRIScloud')
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user2")
        self.assertEqual(
            checkers.APPROVER_NOT_AUTHORIZED,
            checkers.approver_checks(checker)[0][0],
        )

    def test_approver_not_authorized_zero(self):
        data = build_quota('volume', 'gigabytes', 0, 'QRIScloud')
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user2")
        self.assertEqual([], checkers.approver_checks(checker))

    def test_approver_not_authorized_blank(self):
        data = build_quota('volume', 'gigabytes', '', 'QRIScloud')
        form = FakeForm(data)
        checker = build_checker(form=form, approver="test_user2")
        self.assertEqual([], checkers.approver_checks(checker))

    def test_no_grants_not_approving(self):
        checker = build_checker([])
        self.assertIsNone(checkers.grant_checks(checker))

    def test_no_grants_approving_local(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun', national=False
        )
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.grant_checks(checker))

    def test_no_grants_approving_national(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun', national=True
        )
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertEqual(
            checkers.NO_VALID_GRANTS, checkers.grant_checks(checker)[0][0]
        )

    def test_no_grants_special_approving_national(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun',
            national=True,
            special_approval="Fun is special",
        )
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.grant_checks(checker))

    def test_no_grants_ardc_approving_national(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun', national=True
        )
        support = factories.ARDCSupportFactory.create()
        allocation.ardc_support.add(support)
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.grant_checks(checker))

    def test_no_grants_ncris_approving_national(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun', national=True
        )
        facility = factories.NCRISFacilityFactory.create()
        allocation.ncris_facilities.add(facility)
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.grant_checks(checker))

    def test_old_grant_approving_national(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun', national=True
        )
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='ardc',
            last_year_funded=2000,
        )
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertEqual(
            checkers.NO_VALID_GRANTS, checkers.grant_checks(checker)[0][0]
        )

    def test_local_grant_approving_national(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun', national=True
        )
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='inst',
            last_year_funded=20000,
        )
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertEqual(
            checkers.NO_VALID_GRANTS, checkers.grant_checks(checker)[0][0]
        )

    def test_current_grant_approving_national(self):
        allocation = factories.AllocationFactory.create(
            project_name='fun', national=True
        )
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='arc',
            last_year_funded=20000,
        )
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.grant_checks(checker))

    def build_green_allocation(self, **kwargs):
        """Create an allocation that is Green and not flagged National."""
        values = {
            'project_name': 'fun',
            'national': False,
            'data_classification_level': models.AllocationRequest.GREEN,
        }
        values.update(kwargs)
        return factories.AllocationFactory.create(**values)

    def test_national_not_flagged_not_approving(self):
        allocation = self.build_green_allocation()
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='arc',
            last_year_funded=20000,
        )
        checker = build_checker([], allocation=allocation, approve_action=True)
        self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_national_not_flagged_approver_edit_page(self):
        allocation = self.build_green_allocation()
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='arc',
            last_year_funded=20000,
        )
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_national_not_flagged_already_national(self):
        allocation = self.build_green_allocation(national=True)
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='arc',
            last_year_funded=20000,
        )
        checker = build_checker(
            [],
            approver='test_user',
            allocation=allocation,
            approve_action=True,
        )
        self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_national_not_flagged_no_grants_or_support(self):
        allocation = self.build_green_allocation()
        checker = build_checker(
            [],
            approver='test_user',
            allocation=allocation,
            approve_action=True,
        )
        self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_national_not_flagged_current_grant_of_each_type(self):
        for grant_type in checkers.NATIONAL_GRANT_TYPES:
            with self.subTest(grant_type=grant_type):
                allocation = self.build_green_allocation()
                factories.GrantFactory.create(
                    allocation_id=allocation.id,
                    grant_type=grant_type,
                    last_year_funded=20000,
                )
                checker = build_checker(
                    [],
                    approver='test_user',
                    allocation=allocation,
                    approve_action=True,
                )
                res = checkers.national_not_flagged_check(checker)
                self.assertEqual(1, len(res))
                self.assertEqual(checkers.NATIONAL_NOT_FLAGGED, res[0][0])

    def test_national_not_flagged_industry_grant(self):
        allocation = self.build_green_allocation()
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='industry',
            last_year_funded=20000,
        )
        checker = build_checker(
            [],
            approver='test_user',
            allocation=allocation,
            approve_action=True,
        )
        self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_national_not_flagged_old_grant(self):
        allocation = self.build_green_allocation()
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='arc',
            last_year_funded=2000,
        )
        checker = build_checker(
            [],
            approver='test_user',
            allocation=allocation,
            approve_action=True,
        )
        self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_national_not_flagged_ardc_support(self):
        allocation = self.build_green_allocation()
        allocation.ardc_support.add(factories.ARDCSupportFactory.create())
        checker = build_checker(
            [],
            approver='test_user',
            allocation=allocation,
            approve_action=True,
        )
        res = checkers.national_not_flagged_check(checker)
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.NATIONAL_NOT_FLAGGED, res[0][0])

    def test_national_not_flagged_ncris_facility(self):
        allocation = self.build_green_allocation()
        allocation.ncris_facilities.add(
            factories.NCRISFacilityFactory.create()
        )
        checker = build_checker(
            [],
            approver='test_user',
            allocation=allocation,
            approve_action=True,
        )
        res = checkers.national_not_flagged_check(checker)
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.NATIONAL_NOT_FLAGGED, res[0][0])

    def test_national_not_flagged_other_classifications(self):
        levels = [
            models.AllocationRequest.YELLOW,
            models.AllocationRequest.ORANGE,
            models.AllocationRequest.RED,
            models.AllocationRequest.NOT_SURE,
            None,
        ]
        for level in levels:
            with self.subTest(level=level):
                allocation = self.build_green_allocation(
                    data_classification_level=level
                )
                factories.GrantFactory.create(
                    allocation_id=allocation.id,
                    grant_type='arc',
                    last_year_funded=20000,
                )
                checker = build_checker(
                    [],
                    approver='test_user',
                    allocation=allocation,
                    approve_action=True,
                )
                self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_national_not_flagged_form_sets_national(self):
        allocation = self.build_green_allocation()
        factories.GrantFactory.create(
            allocation_id=allocation.id,
            grant_type='arc',
            last_year_funded=20000,
        )
        checker = build_checker(
            FakeForm({'national': True}),
            approver='test_user',
            allocation=allocation,
            approve_action=True,
        )
        self.assertIsNone(checkers.national_not_flagged_check(checker))

    def test_std_organisation(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.organisation_checks(checker))

    def test_unvetted_organisation(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        org = factories.OrganisationFactory.create(
            proposed_by="someone", vetted_by=None
        )
        allocation.supported_organisations.add(org.id)
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        res = checkers.organisation_checks(checker)
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.APPROVER_UNVETTED_ORGANISATION, res[0][0])
        self.assertRegex(res[0][1], f".+{org.full_name}.+{org.proposed_by}.+")

    def test_disabled_organisation(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        org = factories.OrganisationFactory.create(
            proposed_by="someone", enabled=False
        )
        allocation.supported_organisations.add(org.id)
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        res = checkers.organisation_checks(checker)
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.APPROVER_DISABLED_ORGANISATION, res[0][0])
        self.assertRegex(res[0][1], f".+{org.full_name}.+")

    def test_vetted_organisation(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        organisation = factories.OrganisationFactory.create(
            proposed_by="someone",
            vetted_by=models.Approver.objects.get(username="test_user"),
        )
        allocation.supported_organisations.add(organisation.id)
        checker = build_checker(
            [], approver='test_user', allocation=allocation
        )
        self.assertIsNone(checkers.organisation_checks(checker))
