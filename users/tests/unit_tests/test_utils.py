from django.test import TestCase
from django.test.client import RequestFactory

from users.utils import get_ip_address_from_request


class GetIpAddressTests(TestCase):
    """
    Tests for get_ip_address_from_request util method
    """
    def setUp(self):
        """
        Setup the request factory and create a test user
        """
        super(GetIpAddressTests, self).setUp()
        self.rf = RequestFactory()

    def test_get_ip_address_from_request(self):
        """
        Test if an IP address is in the request, it'll be saved on the user object
        """
        test_ip = '210.1.1.1'
        request = self.rf.get('/', REMOTE_ADDR=test_ip)
        ip_address = get_ip_address_from_request(request)
        self.assertEqual(ip_address, test_ip)

    def test_get_ip_address_from_request__without_ip(self):
        """
        Test if an IP address is not present in the request, the method won't blow up
        """
        request = self.rf.get('/')
        ip_address = get_ip_address_from_request(request)
        self.assertEqual(ip_address, None)
