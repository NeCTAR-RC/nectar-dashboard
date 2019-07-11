# Copyright 2019 Australian Research Data Commons
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

import factory
from factory import fuzzy

from nectar_dashboard.user_info import models


def factory_setup():
    pass


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'user_info.User'

    user_id = fuzzy.FuzzyText(length=32, chars="0123456789abcdef")
    displayname = fuzzy.FuzzyText(length=20)
    first_name = fuzzy.FuzzyText(length=10)
    surname = fuzzy.FuzzyText(length=10)
    phone_number = fuzzy.FuzzyText(length=8, chars="123456789", prefix="02")
    mobile_number = fuzzy.FuzzyText(length=8, chars="123456789", prefix="04")
    home_organization = "UoM"
    affiliation = models.MEMBER
    state = models.STATE_REGISTERED
    terms_version = 1
