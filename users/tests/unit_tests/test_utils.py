from django.test import TestCase
from django.test.client import RequestFactory

from users.utils import get_ip_address_from_request


class GetIpAddressTests(TestCase):
    """
    get_ip_address_from_request函数的测试
    """
    def setUp(self):
        """
        创建request工厂，创建测试用户
        """
        super(GetIpAddressTests, self).setUp()
        self.rf = RequestFactory()

    def test_get_ip_address_from_request(self):
        """
        测试当request里包含IP信息的时候，会正确返回IP地址
        """
        test_ip = '210.1.1.1'
        request = self.rf.get('/', REMOTE_ADDR=test_ip)
        ip_address = get_ip_address_from_request(request)
        self.assertEqual(ip_address, test_ip)

    def test_get_ip_address_from_request__without_ip(self):
        """
        测试当request里不包含IP信息的时候，函数仍然会正常返回
        """
        request = self.rf.get('/')
        ip_address = get_ip_address_from_request(request)
        self.assertEqual(ip_address, None)
