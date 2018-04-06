from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.timezone import now, timedelta
from rest_framework import status, test
from rest_framework.reverse import reverse

from balance.models import Record
from posts.models import Post
from replies.api.serializers import FlatReplySerializer
from replies.models import Reply

from ...models import User


class UserViewSetTestCase(test.APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='test',
            nickname='test'
        )

        self.another_user = User.objects.create_user(
            username='another',
            email='another@test.com',
            password='another',
            nickname='another'
        )

        self.site = Site.objects.create(name='test', domain='test.com')
        self.post = Post.objects.create(
            title='test title',
            author=self.another_user
        )
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id

    def test_return_user_replies(self):
        reply1 = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='reply1',
        )
        reply2 = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='reply2',
            parent=reply1
        )
        reply3 = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,
            comment='reply3',
            parent=reply1
        )

        url = reverse('user-replies', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            FlatReplySerializer(
                self.user.reply_comments.filter(is_public=True, is_removed=False),
                many=True
            ).data
        )

    def test_anonymous_user_cannot_checkin(self):
        url = reverse('user-checkin', kwargs={'pk': self.user.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_request_user_can_checkin(self):
        url = reverse('user-checkin', kwargs={'pk': self.user.id})
        self.client.login(username='test', password='test')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 1)
        self.assertEqual(Record.objects.get().user, self.user)

    def test_non_current_request_user_cannot_checkin(self):
        url = reverse('user-checkin', kwargs={'pk': self.another_user.id})
        self.client.login(username='test', password='test')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_only_chekin_once_per_day(self):
        url = reverse('user-checkin', kwargs={'pk': self.user.id})
        self.client.login(username='test', password='test')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 1)
        self.assertEqual(Record.objects.get().user, self.user)

        # 再一次签到
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_checkin_after_a_day(self):
        record = Record.objects.create(
            reward_type=0,
            coin_type=2,
            amount=10,
            description='',
            user=self.user,
        )
        record.created_time = record.created_time - timedelta(days=1)
        record.save()
        record.refresh_from_db()

        url = reverse('user-checkin', kwargs={'pk': self.user.id})
        self.client.login(username='test', password='test')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 2)
