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

from nectar_dashboard.rcallocation import checkers
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


class FakeForm(object):

    def __init__(self, values):
        self.cleaned_data = values


DUMMY_FORM = FakeForm({})


class CheckerTest(base.BaseTestCase):

    def test_empty_checker(self):
        checker = checkers.Checker()
        self.assertIsNone(checker.allocation)
        self.assertIsNone(checker.form)
        self.assertTrue(len(checker.checks) > 0)

    def test_alloc_checker(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        checker = checkers.Checker(allocation=allocation)
        self.assertIsNotNone(checker.allocation)
        self.assertIsNone(checker.form)
        self.assertTrue(len(checker.checks) > 0)
        self.assertEqual('fun', checker.get_field('project_name'))
        self.assertIsNotNone(checker.get_field('project_description'))

    def test_alloc_form_checker(self):
        allocation = factories.AllocationFactory.create(project_name='fun')
        form = FakeForm({'nectar_support': 'not much'})
        checker = checkers.Checker(allocation=allocation, form=form)
        self.assertIsNotNone(checker.allocation)
        self.assertIsNotNone(checker.form)
        self.assertTrue(len(checker.checks) > 0)
        self.assertEqual('fun', checker.get_field('project_name'))
        self.assertEqual('not much', checker.get_field('nectar_support'))
        self.assertIsNotNone(checker.get_field('project_description'))
