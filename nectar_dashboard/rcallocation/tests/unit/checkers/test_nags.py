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

from datetime import datetime

from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import checkers
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


THIS_YEAR = datetime.now().year


class NagCheckerTest(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()

    def test_init(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        form = []
        checker = checkers.Checker(allocation=allocation, form=form)
        self.assertIsNotNone(checker.allocation)
        self.assertIsNotNone(checker.form)
        self.assertTrue(len(checker.checks) > 0)


class NagChecksTest(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()

    def test_survey_check_good(self):
        allocation = factories.AllocationFactory.create()
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.survey_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_survey_check_bad(self):
        allocation = factories.AllocationFactory.create(usage_types=[])
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.survey_check])
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.NO_SURVEY, res[0][0])

    def test_ncris_check_good(self):
        allocation = factories.AllocationFactory.create()
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.ncris_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_ncris_check_good_2(self):
        allocation = factories.AllocationFactory.create(
            ncris_support='legacy value',
            ncris_facilities=['ALA'])
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.ncris_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_ncris_check_bad(self):
        allocation = factories.AllocationFactory.create(
            ncris_support='legacy value',
            ncris_facilities=[])
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.ncris_check])
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.LEGACY_NCRIS, res[0][0])

    def test_ardc_check_good(self):
        allocation = factories.AllocationFactory.create(nectar_support='')
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.ardc_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_ardc_check_good_2(self):
        allocation = factories.AllocationFactory.create(
            nectar_support='legacy value',
            ardc_support=['CVL'])
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.ardc_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_ardc_check_bad(self):
        allocation = factories.AllocationFactory.create(
            nectar_support='legacy value',
            ardc_support=[])
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.ardc_check])
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.LEGACY_ARDC, res[0][0])

    def test_grant_is_good(self):
        allocation = factories.AllocationFactory.create()
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.grant_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_grant_is_good_2(self):
        allocation = factories.AllocationFactory.create()
        factories.GrantFactory.create(
            allocation=allocation,
            last_year_funded=THIS_YEAR)
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.grant_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_grant_is_good_3(self):
        allocation = factories.AllocationFactory.create()
        factories.GrantFactory.create(
            allocation=allocation,
            last_year_funded=(THIS_YEAR - 1))
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.grant_check])
        res = checker.do_checks()
        self.assertEqual(0, len(res))

    def test_grant_is_bad(self):
        allocation = factories.AllocationFactory.create()
        factories.GrantFactory.create(
            allocation=allocation,
            last_year_funded=(THIS_YEAR - 2))
        checker = checkers.NagChecker(allocation=allocation,
                                      checks=[checkers.grant_check])
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.EXPIRED_GRANT, res[0][0])
