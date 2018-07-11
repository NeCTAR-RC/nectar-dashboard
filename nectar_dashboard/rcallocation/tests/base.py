from django.conf import settings
from django.conf.urls import url
from django.conf.urls import include

#from oslo_utils import importutils

from rest_framework.test import APITestCase#, URLPatternsTestCase
#from rest_framework import routers

from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation.tests import utils


#router = routers.DefaultRouter()
#for name, class_str in settings.REST_VIEW_SETS:
#    klass = importutils.import_class(class_str)
#    router.register(name, klass)


class AllocationAPITest(APITestCase):#, URLPatternsTestCase):

    #urlpatterns = [
        #url(r'^api/', include(router.urls)),
        #]

    def setUp(self, *args, **kwargs):
        self.user = utils.get_user()
        self.user2 = utils.get_user(id='user2')
        self.approver_user = utils.get_user(id='approver', roles=['tenantmanager'])
        self.admin_user = utils.get_user(id='admin', roles=['admin'])
        self.allocation = factories.AllocationFactory.create(
            created_by=self.user.id, status='E', create_quotas=False)
        
