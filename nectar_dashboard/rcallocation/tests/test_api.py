from django.conf import settings
from django.urls import reverse
from django.conf.urls import url
from django.conf.urls import include

from oslo_utils import importutils
import mock

from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import routers
from rest_framework.test import force_authenticate

from openstack_auth import user

from openstack_auth.tests import data_v3

from nectar_dashboard.rcallocation import models

from .factories import AllocationFactory
from .common import allocation_to_dict, request_allocation


router = routers.DefaultRouter()
for name, class_str in settings.REST_VIEW_SETS:
    klass = importutils.import_class(class_str)
    router.register(name, klass)


def get_user(id, username, tenant_name, roles):
    return user.User(id=id,
                     user=username,
                     domain_id='default',
                     user_domain_name='Default',
                     tenant_id=tenant_name,
                     tenant_name=tenant_name,
                     service_catalog={},
                     roles=roles,
                     enabled=True,
                     authorized_tenants=[tenant_name,],
                     endpoint=settings.OPENSTACK_KEYSTONE_URL)

    
class AllocationTests(APITestCase, URLPatternsTestCase):

    urlpatterns = [
        url(r'^rest_api/', include(router.urls)),
    ]
    

    #def setupTestData(cls):
    #    self.allocations = [
    #        models.AllocationRequest.objects.create

    def test_list_allocations(self):
        user = get_user('123', 'sam', 'my-project', ['member'])
        self.client.force_authenticate(user=user)
        allocation = AllocationFactory.create(created_by=user.id)
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(1, len(response.data))

    def test_list_allocations_unauthenticated(self):
        allocation = AllocationFactory.create(created_by='456')
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(0, len(response.data))

    def test_list_allocations_negative(self):
        user = get_user('123', 'sam', 'my-project', ['member'])
        self.client.force_authenticate(user=user)
        allocation = AllocationFactory.create(created_by='456')
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(0, len(response.data))

    def test_list_allocations_admin(self):
        user = get_user('123', 'sam', 'my-project', ['admin'])
        self.client.force_authenticate(user=user)
        allocation = AllocationFactory.create(created_by='456')
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(1, len(response.data))



        
