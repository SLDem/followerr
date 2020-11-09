from django.test import TestCase, Client
from django.utils.encoding import force_bytes
from django.urls import reverse

from friends.models import FriendRequest
from user_profile.models import User
from django.test import tag


class BlockingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(email='test1@gmail.com', password='test1', name='test1')
        self.user2 = User.objects.create_user(email='test2@gmail.com', password='test2', name='test2')
        f_request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        to_f_request = FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        self.user1.friends.add(self.user2)
        self.client.force_login(self.user1)

    def test_block_user(self):
        self.client.get(reverse('block_user', kwargs={'pk': self.user2.pk}), follow=True)
        self.assertIn(self.user2, self.user1.blocked_users.all())
        self.assertNotIn(self.user2, self.user1.friends.all())

    def test_block_user_self(self):
        response = self.client.get(reverse('block_user', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertEqual(response.content, force_bytes("You can't block yourself"))

    def test_unblock_user(self):
        self.user1.blocked_users.add(self.user2)
        self.client.get(reverse('unblock_user', kwargs={'pk': self.user2.pk}))
        self.assertEqual(len(self.user1.blocked_users.all()), 0)

    def test_unblock_user_self(self):
        self.user1.blocked_users.add(self.user2)
        response = self.client.get(reverse('unblock_user', kwargs={'pk': self.user1.pk}))
        self.assertEqual(response.content, force_bytes("You can not unblock yourself or someone you did not block"))

    def test_blocked_users(self):
        response = self.client.get(reverse('blocked_users'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('blocked_users.html')

    def test_blocked_users_empty(self):
        response = self.client.get(reverse('blocked_users'), follow=True)
        self.assertIn(force_bytes("You didn't block anyone"), response.content)

    def test_blocked_users_not_empty(self):
        self.user1.blocked_users.add(self.user2)
        response = self.client.get(reverse('blocked_users'), follow=True)
        self.assertIn(force_bytes(self.user2.name), response.content)
