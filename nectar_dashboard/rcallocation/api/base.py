#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOU
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from rest_framework import response
from rest_framework import status
from rest_framework import viewsets

from nectar_dashboard import rest_auth


class NoDestroyViewSet(viewsets.ModelViewSet):

    permission_classes = (rest_auth.ReadOrAdmin,)

    def destroy(self, request, *args, **kwargs):
        # Don't destroy these objects as it will "break" the form
        # representations for current and historic allocation records.
        # Where possible, mark the object as 'disabled'.  Where not
        # possible, coding is probably required to make it possible.
        # (Or ... it is "hack the database" time ...)
        return response.Response(
            {'error': 'Configuration objects should not be destroyed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)
