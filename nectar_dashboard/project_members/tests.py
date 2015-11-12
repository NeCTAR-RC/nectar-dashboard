# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

from django.core.urlresolvers import reverse
from django import http

from mox import IgnoreArg
from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test

from .constants import PROJECTS_ADD_MEMBER_URL as add_member_url
from .constants import PROJECTS_CREATE_URL as create_url
from .constants import PROJECTS_INDEX_URL as index_url
from .constants import PROJECTS_INDEX_VIEW_TEMPLATE
from .constants import PROJECTS_MANAGE_URL as manage_url
from .constants import PROJECTS_MANAGE_VIEW_TEMPLATE
from .constants import PROJECTS_UPDATE_URL as update_url


PROJECTS_INDEX_URL = reverse(index_url)
GROUP_CREATE_URL = reverse(create_url)
GROUP_UPDATE_URL = reverse(update_url, args=[1])
GROUP_MANAGE_URL = reverse(manage_url, args=[1])
GROUP_ADD_MEMBER_URL = reverse(add_member_url, args=[1])


class ProjectsViewTests(test.BaseAdminViewTests):
    @test.create_stubs({api.keystone: ('project_list',)})
    def test_index(self):
        api.keystone.project_list(IgnoreArg()).AndReturn(self.projects.list())

        self.mox.ReplayAll()

        res = self.client.get(PROJECTS_INDEX_URL)

        self.assertTemplateUsed(res, PROJECTS_INDEX_VIEW_TEMPLATE)
        self.assertItemsEqual(res.context['table'].data, self.projects.list())

        self.assertContains(res, 'Create Project')
        self.assertContains(res, 'Edit')
        self.assertContains(res, 'Delete Project')

    @test.create_stubs({api.keystone: ('project_list',
                                       'keystone_can_edit_project')})
    def test_index_with_keystone_can_edit_project_false(self):
        api.keystone.project_list(IgnoreArg()).AndReturn(self.projects.list())
        api.keystone.keystone_can_edit_project() \
            .MultipleTimes().AndReturn(False)

        self.mox.ReplayAll()

        res = self.client.get(PROJECTS_INDEX_URL)

        self.assertTemplateUsed(res, PROJECTS_INDEX_VIEW_TEMPLATE)
        self.assertItemsEqual(res.context['table'].data, self.projects.list())

        self.assertNotContains(res, 'Create Project')
        self.assertNotContains(res, 'Edit')
        self.assertNotContains(res, 'Delete Project')

    @test.create_stubs({api.keystone: ('project_create', )})
    def test_create(self):
        project = self.projects.get(id="1")

        api.keystone.project_create(IsA(http.HttpRequest),
                                  description=project.description,
                                  domain_id=None,
                                  name=project.name).AndReturn(project)

        self.mox.ReplayAll()

        formData = {'method': 'CreateProjectForm',
                    'name': project.name,
                    'description': project.description}
        res = self.client.post(GROUP_CREATE_URL, formData)

        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

    @test.create_stubs({api.keystone: ('project_get',
                                       'project_update')})
    def test_update(self):
        project = self.projects.get(id="1")
        test_description = 'updated description'

        api.keystone.project_get(IsA(http.HttpRequest), '1').AndReturn(project)
        api.keystone.project_update(IsA(http.HttpRequest),
                                  description=test_description,
                                  project_id=project.id,
                                  name=project.name).AndReturn(None)

        self.mox.ReplayAll()

        formData = {'method': 'UpdateProjectForm',
                    'project_id': project.id,
                    'name': project.name,
                    'description': test_description}

        res = self.client.post(GROUP_UPDATE_URL, formData)

        self.assertNoFormErrors(res)

    @test.create_stubs({api.keystone: ('project_list',
                                       'project_delete')})
    def test_delete_project(self):
        project = self.projects.get(id="2")

        api.keystone.project_list(IgnoreArg()).AndReturn(self.projects.list())
        api.keystone.project_delete(IgnoreArg(), project.id)

        self.mox.ReplayAll()

        formData = {'action': 'projects__delete__%s' % project.id}
        res = self.client.post(PROJECTS_INDEX_URL, formData)

        self.assertRedirectsNoFollow(res, PROJECTS_INDEX_URL)

    @test.create_stubs({api.keystone: ('project_get',
                                       'user_list',)})
    def test_manage(self):
        project = self.projects.get(id="1")
        project_members = self.users.list()

        api.keystone.project_get(IsA(http.HttpRequest), project.id).\
            AndReturn(project)
        api.keystone.user_list(IgnoreArg(),
                               project=project.id).\
            AndReturn(project_members)
        self.mox.ReplayAll()

        res = self.client.get(GROUP_MANAGE_URL)

        self.assertTemplateUsed(res, PROJECTS_MANAGE_VIEW_TEMPLATE)
        self.assertItemsEqual(res.context['table'].data, project_members)

    @test.create_stubs({api.keystone: ('user_list',
                                       'remove_project_user')})
    def test_remove_user(self):
        project = self.projects.get(id="1")
        user = self.users.get(id="2")

        api.keystone.user_list(IgnoreArg(),
                               project=project.id).\
            AndReturn(self.users.list())
        api.keystone.remove_project_user(IgnoreArg(),
                                       project_id=project.id,
                                       user_id=user.id)
        self.mox.ReplayAll()

        formData = {'action': 'project_members__removeProjectMember__%s' % user.id}
        res = self.client.post(GROUP_MANAGE_URL, formData)

        self.assertRedirectsNoFollow(res, GROUP_MANAGE_URL)
        self.assertMessageCount(success=1)

    @test.create_stubs({api.keystone: ('project_get',
                                       'user_list',
                                       'add_project_user')})
    def test_add_user(self):
        project = self.projects.get(id="1")
        user = self.users.get(id="2")

        api.keystone.project_get(IsA(http.HttpRequest), project.id).\
            AndReturn(project)
        api.keystone.user_list(IgnoreArg(),
                               domain=project.domain_id).\
            AndReturn(self.users.list())
        api.keystone.user_list(IgnoreArg(),
                               project=project.id).\
            AndReturn(self.users.list()[2:])

        api.keystone.add_project_user(IgnoreArg(),
                                    project_id=project.id,
                                    user_id=user.id)

        self.mox.ReplayAll()

        formData = {'action': 'project_non_members__addMember__%s' % user.id}
        res = self.client.post(GROUP_ADD_MEMBER_URL, formData)

        self.assertRedirectsNoFollow(res, GROUP_MANAGE_URL)
        self.assertMessageCount(success=1)
