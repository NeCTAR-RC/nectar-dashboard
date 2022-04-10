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

PANEL_GROUP = 'usage'
PANEL_DASHBOARD = 'project'
PANEL = 'trend'

# Python panel class of the PANEL to be added.
ADD_PANEL = \
    'nectar_dashboard.usage.trend.panel.Trend'

ADD_INSTALLED_APPS = ['nectar_dashboard.usage.trend']
