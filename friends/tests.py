from django.test import TestCase, Client, tag
from django.utils.encoding import force_bytes
from django.urls import reverse

from .models import FriendRequest

from user_profile.models import User


class FriendsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', name='test', password='test')
        self.user1 = User.objects.create_user(email='test1@gmail.com', name='test1', password='test1')
        self.friend_request = FriendRequest.objects.create(from_user=self.user, to_user=self.user1)

    def test_friend_request_creation(self):
        friends_request = FriendRequest.objects.create(from_user=self.user, to_user=self.user1)
        self.assertTrue(isinstance(friends_request, FriendRequest))

    def test_friends_request_deletion(self):
        FriendRequest.objects.filter(from_user=self.user, to_user=self.user1).first().delete()
        self.assertEqual(len(FriendRequest.objects.all()), 0)

    def tearDown(self):
        self.user.delete()
        self.user1.delete()


class FriendsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', name='test', password='test')
        self.user1 = User.objects.create_user(email='test1@gmail.com', name='test1', password='test1')
        self.client.force_login(self.user)

    def test_friends_view(self):
        response = self.client.get(reverse('friends', kwargs={'pk': self.user.pk}), follow=True)
        self.assertTemplateUsed(response, 'friends.html')
        self.assertEqual(response.status_code, 200)

    def test_friends_view_doesnt_exist(self):
        response = self.client.get(reverse('friends', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('User does not exist'), response.content)

    def test_send_friend_request(self):
        self.client.get(reverse('send_friend_request', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertTrue(isinstance(FriendRequest.objects.filter(from_user=self.user, to_user=self.user1).first(), FriendRequest))

    def test_send_friend_request_user_doesnt_exist(self):
        response = self.client.get(reverse('send_friend_request', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('User does not exist'), response.content)

    def test_send_friend_request_friend_request_exists_from_other_user(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user)
        self.client.get(reverse('send_friend_request', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertIn(self.user1, self.user.friends.all())
        self.assertIn(self.user, self.user1.friends.all())

    def test_cancel_friend_request(self):
        FriendRequest.objects.create(from_user=self.user, to_user=self.user1)
        self.client.get(reverse('cancel_friend_request', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertFalse(isinstance(FriendRequest.objects.filter(from_user=self.user, to_user=self.user1).first(), FriendRequest))

    def test_cancel_friend_request_user_doesnt_exist(self):
        response = self.client.get(reverse('cancel_friend_request', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('User does not exist'), response.content)

    def test_accept_friend_request(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user)
        response = self.client.get(reverse('accept_friend_request', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertIn(self.user1, self.user.friends.all())
        self.assertIn(self.user, self.user1.friends.all())

    def test_delete_friend_request(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user)
        self.client.get(reverse('delete_friend_request', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertEqual(len(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user)), 0)

    def test_delete_friend_request_user_doesnt_exist(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user)
        response = self.client.get(reverse('delete_friend_request', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('User does not exist'), response.content)


    def test_remove_friend(self):
        self.user1.friends.add(self.user)
        self.user.friends.add(self.user1)
        self.client.get(reverse('remove_friend', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertNotIn(self.user, self.user1.friends.all())
        self.assertNotIn(self.user1, self.user.friends.all())

    def test_remove_friend_user_doesnt_exist(self):
        response = self.client.get(reverse('remove_friend', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('User does not exist'), response.content)
