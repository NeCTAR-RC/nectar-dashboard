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


from nectar_dashboard.rcallocation import checkers
from nectar_dashboard.rcallocation import output_type_choices
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


THIS_YEAR = datetime.now().year


class NagCheckerTest(base.BaseTestCase):

    def test_init(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        checker = checkers.NagChecker(allocation=allocation)
        self.assertEqual(allocation, checker.allocation)
        self.assertIsNone(checker.form)
        self.assertTrue(len(checker.CHECKS) > 0)


CUTOFF = checkers.EXPIRED_GRANT_CUTOFF_YEARS


class NagChecksTest(base.BaseTestCase):

    def test_survey_check_good(self):
        allocation = factories.AllocationFactory.create()
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_survey_check_bad(self):
        allocation = factories.AllocationFactory.create(usage_types=[])
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.NO_SURVEY, res[0][0])

    def test_ncris_check_good(self):
        allocation = factories.AllocationFactory.create()
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_ncris_check_good_2(self):
        allocation = factories.AllocationFactory.create(
            ncris_support='legacy value',
            ncris_facilities=['ALA'])
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_ncris_check_bad(self):
        allocation = factories.AllocationFactory.create(
            ncris_support='legacy value',
            ncris_facilities=[])
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.LEGACY_NCRIS, res[0][0])

    def test_ardc_check_good(self):
        allocation = factories.AllocationFactory.create(nectar_support='')
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_ardc_check_good_2(self):
        allocation = factories.AllocationFactory.create(
            nectar_support='legacy value',
            ardc_support=['CVL'])
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_ardc_check_bad(self):
        allocation = factories.AllocationFactory.create(
            nectar_support='legacy value',
            ardc_support=[])
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.LEGACY_ARDC, res[0][0])

    def test_no_grants(self):
        allocation = factories.AllocationFactory.create()
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_grant_current(self):
        allocation = factories.AllocationFactory.create()
        factories.GrantFactory.create(
            allocation=allocation,
            last_year_funded=THIS_YEAR)
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_grant_current_2(self):
        allocation = factories.AllocationFactory.create()
        factories.GrantFactory.create(
            allocation=allocation,
            last_year_funded=(THIS_YEAR - CUTOFF + 1))
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_grant_expired(self):
        allocation = factories.AllocationFactory.create()
        factories.GrantFactory.create(
            allocation=allocation,
            last_year_funded=(THIS_YEAR - CUTOFF))
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.EXPIRED_GRANT, res[0][0])

    def test_no_output(self):
        allocation = factories.AllocationFactory.create()
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_output_ok(self):
        allocation = factories.AllocationFactory.create()
        factories.PublicationFactory.create(
            allocation=allocation,
            output_type=output_type_choices.DATASET)
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)

    def test_output_unspecified(self):
        allocation = factories.AllocationFactory.create()
        factories.PublicationFactory.create(
            allocation=allocation,
            output_type=output_type_choices.UNSPECIFIED)
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.UNSPECIFIED_OUTPUT, res[0][0])

    def test_output_no_crossref(self):
        allocation = factories.AllocationFactory.create()
        factories.PublicationFactory.create(
            allocation=allocation,
            crossref_metadata="",
            output_type=output_type_choices.PEER_REVIEWED_JOURNAL_ARTICLE)
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual(1, len(res))
        self.assertEqual(checkers.NO_CROSSREF, res[0][0])

    def test_output_has_crossref(self):
        allocation = factories.AllocationFactory.create()
        factories.PublicationFactory.create(
            allocation=allocation,
            crossref_metadata="{'foo': 'bar'}",    # fake ...
            output_type=output_type_choices.PEER_REVIEWED_JOURNAL_ARTICLE)
        checker = checkers.NagChecker(allocation=allocation)
        res = checker.do_checks()
        self.assertEqual([], res)
