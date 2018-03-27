from django.test import TestCase
from django.test.client import RequestFactory

from users.models import User, update_last_login_ip


class UserSignalTests(TestCase):
    """
    Tests for user signal related methods
    """
    def setUp(self):
        """
        Setup the request factory and create a test user
        """
        super(UserSignalTests, self).setUp()
        self.rf = RequestFactory()
        self.user = User.objects.create(nickname='test-user', username='test-user')

    def test_update_last_login_ip(self):
        """
        Test if an IP address is in the request, it'll be saved on the user object
        """
        test_ip = '210.1.1.1'
        request = self.rf.get('/', REMOTE_ADDR=test_ip)
        update_last_login_ip(None, self.user, request)
        self.assertEqual(self.user.last_login_ip, test_ip)

    def test_update_last_login_ip__without_ip(self):
        """
        Test if an IP address is not present in the request, the method won't blow up
        """
        request = self.rf.get('/')
        update_last_login_ip(None, self.user, request)
        self.assertEqual(self.user.last_login_ip, None)
