from django.test import TestCase

from users.models import User
from users.serializers import UserDetailsSerializer


class UserDetailsSerializerTests(TestCase):
    """
    用户详细信息序列器的测试
    """
    def setUp(self):
        """
        创建测试用户
        """
        super(UserDetailsSerializerTests, self).setUp()
        self.user = User.objects.create(nickname='test-user', username='test-user')

    def test_serialize_user_details(self):
        """
        测试序列化用户实例
        """
        serializer = UserDetailsSerializer(self.user)
        serialized_data = serializer.data
        self.assertEqual(serialized_data['id'], self.user.id)
        self.assertEqual(serialized_data['username'], self.user.username)
        self.assertEqual(serialized_data['nickname'], self.user.nickname)
        self.assertEqual(serialized_data['ip_joined'], self.user.ip_joined)
        self.assertEqual(serialized_data['last_login_ip'], self.user.last_login_ip)
        self.assertEqual(serialized_data['is_superuser'], self.user.is_superuser)
        self.assertEqual(serialized_data['is_staff'], self.user.is_staff)
        self.assertEqual(serialized_data['post_count'], self.user.post_set.count())
        self.assertEqual(serialized_data['reply_count'], self.user.reply_comments.count())
