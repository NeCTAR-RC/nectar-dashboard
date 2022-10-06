# Copyright 2023 Australian Research Data Commons
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

from django.template import Library
from nectar_dashboard.rcallocation import models


register = Library()


@register.filter()
def org_status(organisation):
    if not organisation.ror_id and organisation.full_name in [
            models.ORG_ALL_FULL_NAME, models.ORG_UNKNOWN_FULL_NAME]:
        return ""
    elif organisation.enabled:
        if organisation.ror_id or organisation.vetted_by:
            return ""
        else:
            return " - Waiting for vetting of proposed organisation"
    else:
        if organisation.ror_id:
            return " - Invalid - organisation withdrawn from ROR"
        else:
            return " - Invalid - proposed organisation failed vetting"
