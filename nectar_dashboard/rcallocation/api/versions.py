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

from rest_framework import response
from rest_framework import viewsets

from nectar_dashboard.rcallocation import api


class VersionsViewSet(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        version_info = {
            "versions": [
                {
                    "id": f"v{api.CURRENT_VERSION}",
                    "status": "CURRENT",
                    "version": f"{api.CURRENT_VERSION}",
                }
            ]
        }
        return response.Response(version_info)
