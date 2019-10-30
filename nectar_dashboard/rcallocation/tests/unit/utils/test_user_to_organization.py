from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils


class UserToOrganizationTest(helpers.TestCase):

    def setUp(self):
        super(UserToOrganizationTest, self).setUp()
        x = models.Organization.objects.create(name='X')
        models.EmailDomain.objects.create(domain="a.b.c", organization=x)
        models.EmailDomain.objects.create(domain="d.b.c", organization=x)
        y = models.Organization.objects.create(name='Y')
        models.EmailDomain.objects.create(domain="r", organization=y)

    def test_user_to_organization(self):
        x = models.Organization.objects.get(name='X')
        y = models.Organization.objects.get(name='Y')
        self.assertIsNone(utils.user_to_organization("fred@s.p.q.z"))
        self.assertEqual(y, utils.user_to_organization("fred@s.p.q.r"))
        self.assertEqual(x, utils.user_to_organization("fred@a.b.c"))
        self.assertEqual(x, utils.user_to_organization("fred@0.a.b.c"))
        self.assertEqual(x, utils.user_to_organization("fred@d.b.c"))
        self.assertIsNone(utils.user_to_organization("fred@b.c"))
        with self.assertRaises():
            utils.user_to_organization("fred")
        with self.assertRaises():
            utils.user_to_organization("@a.b.c")
        with self.assertRaises():
            utils.user_to_organization("fred@")
        with self.assertRaises():
            utils.user_to_organization("fred@@a.b.c")
        with self.assertRaises():
            utils.user_to_organization("@")
