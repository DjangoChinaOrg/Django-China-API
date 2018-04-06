from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from ..models import Post
from ..serializers import IndexPostListSerializer
from users.models import User
from tags.models import Tag


class PostSerializerTests(TestCase):
    """
    测试帖子序列化器
    """
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.tag1 = Tag.objects.create(name='test_tag',
                                      creator=self.user)
        self.tag2 = Tag.objects.create(name='another test_tag',
                                       creator=self.user)
        self.post = Post.objects.create(title='test title first',
                                         body='first test body',
                                         author=self.user
                                         )
        self.post.tags.add(self.tag1)
        self.post.tags.add(self.tag2)

    def test_post_serializer_detail(self):
        serializer = IndexPostListSerializer(self.post, context={'request': None})
        data = serializer.data
        self.assertEqual(data['id'], self.post.id)
        self.assertEqual(data['title'], self.post.title)
        self.assertEqual(data['views'], self.post.views)
        self.assertEqual(data['pinned'], self.post.pinned)
        self.assertEqual(data['highlighted'], self.post.highlighted)
        self.assertEqual(data['reply_count'], self.post.replies.count())
