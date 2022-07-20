from openstack_dashboard.test import helpers as test

from nectar_dashboard import api
from nectar_dashboard.api.rest import usage


class UsageRestTestCase(test.TestCase):

    @test.create_mocks({api.usage: ['get_summary']})
    def test_summary(self):
        request = self.mock_rest_request(**{'GET': {}})
        self.mock_get_summary.return_value = '{}'
        response = usage.Summary().get(request)
        self.assertStatusCode(response, 200)
        self.mock_get_summary.assert_called_once_with(request, filters={},
                                                      detailed=False)

    @test.create_mocks({api.usage: ['get_summary']})
    def test_summary_detailed(self):
        request = self.mock_rest_request(**{'GET': {'detailed': True}})
        self.mock_get_summary.return_value = '{}'
        response = usage.Summary().get(request)
        self.assertStatusCode(response, 200)
        self.mock_get_summary.assert_called_once_with(request, filters={},
                                                      detailed=True)

    @test.create_mocks({api.usage: ['get_summary']})
    def test_summary_type_filter(self):
        request = self.mock_rest_request(**{'GET': {'type': 'instance'}})
        self.mock_get_summary.return_value = '{}'
        response = usage.Summary().get(request)
        self.assertStatusCode(response, 200)
        self.mock_get_summary.assert_called_once_with(
            request, filters={'type': 'instance'}, detailed=False)

    @test.create_mocks({api.usage: ['get_summary']})
    def test_summary_by_type(self):
        request = self.mock_rest_request(**{'GET': {}})
        self.mock_get_summary.return_value = '{}'
        response = usage.SummaryByType().get(request, 'instance')
        self.assertStatusCode(response, 200)
        self.mock_get_summary.assert_called_once_with(
            request, filters={'type': 'instance'}, detailed=False)
