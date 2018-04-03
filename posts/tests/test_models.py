from django.test import TestCase

from ..models import Post
from users.models import User
from tags.models import Tag


class PostModelTests(TestCase):
    """
    测试Post的objects和public manager
    """

    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.tag = Tag.objects.create(name='test_tag',
                                      creator=self.user)

    def test_managers(self):
        self.post1 = Post.objects.create(title='test title first',
                                         body='first test body',
                                         author=self.user
                                         )
        self.post1.tags.add(self.tag)
        self.post2 = Post.objects.create(title='test title second',
                                         body='second test body',
                                         author=self.user,
                                         hidden=True
                                         )
        self.post2.tags.add(self.tag)
        self.assertEqual(Post.objects.all().count(), 2)
        self.assertEqual(Post.public.all().count(), 1)
        self.assertEqual(Post.public.get().hidden, False)
