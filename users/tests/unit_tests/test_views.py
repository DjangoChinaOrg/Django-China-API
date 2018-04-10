from allauth.account.models import EmailAddress
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

    def test_user_can_get_non_hidden_posts(self):
        Post.objects.create(
            title='test',
            author=self.user,
        )

        Post.objects.create(
            title='test2',
            author=self.user,
        )

        Post.objects.create(
            title='test3',
            author=self.user,
        )

        Post.objects.create(
            title='test4',
            author=self.user,
            hidden=True
        )

        url = reverse('user-posts', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_user_can_only_get_self_hidden_posts(self):
        Post.objects.create(
            title='test',
            author=self.user,
        )

        Post.objects.create(
            title='test',
            author=self.user,
            hidden=True
        )

        Post.objects.create(
            title='test',
            author=self.another_user,
            hidden=True
        )

        url = reverse('user-posts', kwargs={'pk': self.user.id})
        response = self.client.get(url, {'hidden': 'true'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='test', password='test')
        response = self.client.get(url, {'hidden': 'true'})
        self.assertEqual(len(response.data), 1)

        other_url = reverse('user-posts', kwargs={'pk': self.another_user.id})
        response = self.client.get(other_url, {'hidden': 'true'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_get_user_treasure(self):
        Record.objects.create(
            reward_type=0,
            coin_type=2,
            amount=10,
            user=self.user,
        )
        Record.objects.create(
            reward_type=0,
            coin_type=2,
            amount=25,
            user=self.user,
        )
        Record.objects.create(
            reward_type=0,
            coin_type=1,
            amount=10,
            user=self.user,
        )
        Record.objects.create(
            reward_type=0,
            coin_type=1,
            amount=35,
            user=self.user,
        )
        Record.objects.create(
            reward_type=0,
            coin_type=0,
            amount=35,
            user=self.user,
        )
        Record.objects.create(
            reward_type=0,
            coin_type=0,
            amount=35,
            user=self.another_user,
        )
        url = reverse('user-balance', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(list(response.data), [
            {'coin_type': 0, 'amount__sum': 35},
            {'coin_type': 1, 'amount__sum': 45},
            {'coin_type': 2, 'amount__sum': 35},
        ])


class EmailAddressViewSetTestCase(test.APITestCase):
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

        self.email = EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True
        )

        self.unverified_email = EmailAddress.objects.create(
            user=self.user,
            email='unverified@test.com',
            verified=False,
            primary=False
        )

        self.another_user_email = EmailAddress.objects.create(
            user=self.another_user,
            email=self.another_user.email,
            verified=True,
            primary=True
        )

    def test_anonymous_user_cannot_operate_email(self):
        list_url = reverse('email-list')
        retrieve_url = reverse('email-detail', kwargs={'pk': self.email.id})
        set_primary_url = reverse('email-set-primary', kwargs={'pk': self.email.id})
        reverify_url = reverse('email-reverify', kwargs={'pk': self.email.id})

        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(list_url, data={
            'user': self.user,
            'email': 'new@email.com',
            'verified': True,
            'primary': True
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(list_url, data={'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(set_primary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(reverify_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_get_self_email(self):
        url = reverse('email-list')
        self.client.login(username='test', password='test')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(
            all([ret['user'] == self.user.id for ret in response.data])
        )

    def test_user_cannnot_get_others_email(self):
        url = reverse('email-detail', kwargs={'pk': self.another_user_email.id})
        self.client.login(username='test', password='test')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_add_email(self):
        url = reverse('email-list')
        self.client.login(username='test', password='test')
        response = self.client.post(url, data={
            'user': self.user,
            'email': 'new@email.com',
            'verified': True,
            'primary': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.emailaddress_set.count(), 3)

    def test_user_cannot_set_unverified_email_to_primary(self):
        url = reverse('email-set-primary', kwargs={'pk': self.unverified_email.id})
        self.client.login(username='test', password='test')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_set_verified_email_to_primary(self):
        verified_unprimary_email = EmailAddress.objects.create(
            user=self.user,
            email='verified_unprimary_email@test.com',
            verified=True,
            primary=False
        )
        url = reverse('email-set-primary', kwargs={'pk': verified_unprimary_email.id})
        self.client.login(username='test', password='test')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 新的 primary email 设置成功
        new_primary_email = EmailAddress.objects.get(pk=verified_unprimary_email.id)
        self.assertTrue(new_primary_email.primary)

        # 旧的 primary email 被设置为非 primary email
        old_primary_email = EmailAddress.objects.get(pk=self.email.id)
        self.assertFalse(old_primary_email.primary)

    def test_can_delete_non_primary_email(self):
        url = reverse('email-detail', kwargs={'pk': self.unverified_email.id})
        self.client.login(username='test', password='test')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.emailaddress_set.count(), 1)

    def test_user_cannot_delete_primary_email(self):
        url = reverse('email-detail', kwargs={'pk': self.email.id})
        self.client.login(username='test', password='test')
        response = self.client.delete(url, data={'email': self.email.email})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.user.emailaddress_set.count(), 2)

    def test_user_cannot_delete_others_email(self):
        url = reverse('email-detail', kwargs={'pk': self.another_user_email.id})
        self.client.login(username='test', password='test')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.another_user.emailaddress_set.count(), 1)

    def test_user_can_reverify_email(self):
        url = reverse('email-reverify', kwargs={'pk': self.email.id})
        self.client.login(username='test', password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
