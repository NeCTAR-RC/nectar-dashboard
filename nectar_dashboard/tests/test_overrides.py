from unittest import mock

from openstack_dashboard.test import helpers as test

from nectar_dashboard import overrides


def _cluster(uuid):
    return mock.Mock(**{'to_dict.return_value': {'uuid': uuid}})


def _risk(resource_id):
    risk_type = mock.MagicMock(
        description='Upgrade your cluster',
        help_url='https://example.com/upgrade',
    )
    risk_type.name = 'kubernetes-eol'
    risk_type.__str__.return_value = 'Kubernetes version end of life'
    return mock.Mock(id='risk-1', resource_id=resource_id, type=risk_type)


EXPECTED_RISK = {
    'id': 'risk-1',
    'type': {
        'name': 'kubernetes-eol',
        'display_name': 'Kubernetes version end of life',
        'description': 'Upgrade your cluster',
        'help_url': 'https://example.com/upgrade',
    },
}


class ClusterSecurityRisksTestCase(test.RestAPITestCase):
    """overrides.py replaces magnum-ui's clusters list REST view with
    _clusters_get_with_risks, which attaches varroa security risks to
    each cluster.
    """

    @mock.patch.object(overrides, 'security')
    @mock.patch.object(overrides.magnum_rest, 'magnum')
    def test_clusters_get_includes_risks(self, magnum, security):
        request = self.mock_rest_request()
        magnum.cluster_list.return_value = [
            _cluster('cluster-1'),
            _cluster('cluster-2'),
        ]
        security.get_security_risks.return_value = [_risk('cluster-1')]

        response = overrides._clusters_get_with_risks(None, request)

        self.assertStatusCode(response, 200)
        items = response.json['items']
        self.assertEqual([EXPECTED_RISK], items[0]['security_risks'])
        self.assertEqual([], items[1]['security_risks'])
        security.get_security_risks.assert_called_once_with(
            request, resource_type='cluster'
        )

    @mock.patch.object(overrides, 'security')
    @mock.patch.object(overrides.magnum_rest, 'magnum')
    def test_clusters_get_varroa_error(self, magnum, security):
        # A varroa outage must not break the clusters panel.
        request = self.mock_rest_request()
        magnum.cluster_list.return_value = [_cluster('cluster-1')]
        security.get_security_risks.side_effect = Exception('varroa down')

        response = overrides._clusters_get_with_risks(None, request)

        self.assertStatusCode(response, 200)
        self.assertEqual([], response.json['items'][0]['security_risks'])

    @mock.patch.object(overrides.magnum_rest, 'magnum')
    def test_clusters_get_no_varroa(self, magnum):
        # varroa-dashboard not installed: security is None.
        request = self.mock_rest_request()
        magnum.cluster_list.return_value = [_cluster('cluster-1')]

        with mock.patch.object(overrides, 'security', None):
            response = overrides._clusters_get_with_risks(None, request)

        self.assertStatusCode(response, 200)
        self.assertEqual([], response.json['items'][0]['security_risks'])
