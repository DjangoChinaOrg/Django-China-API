from django.test import TestCase
from django.test.client import RequestFactory

from users.models import User, update_last_login_ip


class UserSignalTests(TestCase):
    """
    用户信号函数的测试
    """
    def setUp(self):
        """
        创建request工厂，创建测试用户
        """
        super(UserSignalTests, self).setUp()
        self.rf = RequestFactory()
        self.user = User.objects.create(nickname='test-user', username='test-user')

    def test_update_last_login_ip(self):
        """
        测试当request里包含IP信息的时候，会被成功存入用户的last_login_ip域
        """
        test_ip = '210.1.1.1'
        request = self.rf.get('/', REMOTE_ADDR=test_ip)
        update_last_login_ip(None, self.user, request)
        self.assertEqual(self.user.last_login_ip, test_ip)

    def test_update_last_login_ip__without_ip(self):
        """
        测试当request里不包含IP信息的时候，这个函数仍然会正常返回
        """
        request = self.rf.get('/')
        update_last_login_ip(None, self.user, request)
        self.assertEqual(self.user.last_login_ip, None)
