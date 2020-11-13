from django.test import TestCase, Client, tag
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import User
from friends.models import FriendRequest
from posts.models import Post
from photoalbums.models import Image, Photoalbum

from posts.forms import NewPostForm
from photoalbums.forms import NewImageForm
from .forms import EditUserForm, ChangePasswordForm

from Followerr.settings import MEDIA_ROOT

import os

USER_PROFILE_DIR = os.path.dirname(os.path.abspath(__file__))
test_image_path = os.path.join(USER_PROFILE_DIR, 'test.jpg')


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name='test', email='test@gmail.com', password='test')
        self.client.force_login(self.user)

    def test_user_creation(self):
        user = User.objects.create_user(name='test1', email='test1@gmail.com', password='test1')
        self.assertTrue(isinstance(user, User))

    def test_user_deletion(self):
        self.user.delete()
        self.assertEqual(len(User.objects.filter(name='test')), 0)

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), reverse('profile', kwargs={'pk': self.user.pk}))

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(name='stest', email='stest@gmail.com', password='stest')
        self.assertTrue(isinstance(superuser, User))
        self.assertTrue(superuser.is_superuser)


class TestUserView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name='test', email='test@gmail.com', password='test')
        self.user1 = User.objects.create_user(name='test1', email='test1@gmail.com', password='test1')
        self.client.force_login(self.user)
        self.image = SimpleUploadedFile(name='test_image.jpg', content=open(test_image_path, 'rb').read(),
                                        content_type='image/jpg')

    def test_profile_view(self):
        response = self.client.get(reverse('profile', kwargs={'pk': self.user.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_profile_view_fail(self):
        response = self.client.get(reverse('profile', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('User does not exist'), response.content)

    def test_blocked_profile_view(self):
        self.user1.blocked_users.add(self.user)
        response = self.client.get(reverse('profile', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('This user blocked you.'), response.content)

    def test_button_status(self):
        response = self.client.get(reverse('profile', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('Add Friend'), response.content)

        self.user.friends.add(self.user1)
        response = self.client.get(reverse('profile', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('Remove Friend'), response.content)

        self.user.friends.remove(self.user1)
        FriendRequest.objects.create(from_user=self.user, to_user=self.user1)
        response = self.client.get(reverse('profile', kwargs={'pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('Cancel Request'), response.content)

    def test_new_post(self):
        data = {'body': 'test_post'}
        response = self.client.post(reverse('profile', kwargs={'pk': self.user.pk}), data=data, follow=True)
        self.assertIn(force_bytes('test_post'), response.content)

    def test_new_post_fail(self):
        data = {'body': 'test_post'}
        response = self.client.post(reverse('profile', kwargs={'pk': self.user1.pk}), data=data, follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_upload_avatar_view(self):
        response = self.client.get(reverse('upload_avatar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('upload_avatar.html')

    def test_upload_avatar(self):
        data = {'description': 'test_avatar', 'image': self.image}
        self.client.post(reverse('upload_avatar'), data=data)
        avatar = Image.objects.get(description='test_avatar')
        self.user.refresh_from_db()
        self.assertEqual(avatar, self.user.image)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_upload_avatar_album_exists(self):
        Photoalbum.objects.create(title='Profile pictures', user=self.user)
        data = {'description': 'test_avatar', 'image': self.image}
        self.client.post(reverse('upload_avatar'), data=data)
        avatar = Image.objects.get(description='test_avatar')
        self.user.refresh_from_db()
        self.assertEqual(avatar, self.user.image)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_edit_user_view(self):
        response = self.client.get(reverse('edit_user', kwargs={'pk': self.user.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('edit_user.html')

    def test_edit_user(self):
        data = {'email': 'test2@gmail.com',
                'name': 'test2',
                'about_me': 'test2',
                'favourite_music': 'test2',
                'favourite_books': 'test2',
                'favourite_movies': 'test2',
                'gender': True,
                'city': 'Trent',
                'following': 'Kali'}
        self.client.post(reverse('edit_user', kwargs={'pk': self.user.pk}), data=data, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test2@gmail.com')
        self.assertEqual(self.user.name, 'test2')
        self.assertEqual(self.user.about_me, 'test2')
        self.assertEqual(self.user.favourite_music, 'test2')
        self.assertEqual(self.user.favourite_books, 'test2')
        self.assertEqual(self.user.favourite_movies, 'test2')
        self.assertEqual(self.user.gender, True)
        self.assertEqual(self.user.city, 'Trent')
        self.assertEqual(self.user.following, 'Kali')

    def test_edit_user_not_allowed(self):
        data = {'email': 'test2@gmail.com',
                'name': 'test2',
                'about_me': 'test2',
                'favourite_music': 'test2',
                'favourite_books': 'test2',
                'favourite_movies': 'test2',
                'gender': True,
                'city': 'Trent',
                'following': 'Kali'}
        response = self.client.post(reverse('edit_user', kwargs={'pk': self.user1.pk}), data=data, follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_edit_user_fail(self):
        response = self.client.post(reverse('edit_user', kwargs={'pk': '10'}), data={}, follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_change_password_view(self):
        response = self.client.get(reverse('change_password'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('edit_password.html')

    def test_change_password_valid(self):
        prev_pass = self.user.password
        data = {'password': 'test_pass',
                'confirm_password': 'test_pass'}
        self.client.post(reverse('change_password'), data=data, follow=True)
        self.user.refresh_from_db()
        self.assertNotEqual(prev_pass, self.user.password)

    def test_change_password_invalid(self):
        prev_pass = self.user.password
        data = {'password': 'test_pass',
                'confirm_password': 'test_pas'}
        response = self.client.post(reverse('change_password'), data=data, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(prev_pass, self.user.password)
        self.assertIn(force_bytes('Your passwords do not match'), response.content)


class UserFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name='test', email='test@gmail.com', password='test')
        self.client.force_login(self.user)

    def test_edit_user_form_valid(self):
        data = {'email': 'test1@gmail.com',
                'name': 'test1',
                'about_me': 'test',
                'favourite_music': 'test',
                'favourite_books': 'test',
                'favourite_movies': 'test',
                'gender': True,
                'city': 'Trent',
                'following': 'Kali'}
        form = EditUserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_edit_user_form_invalid(self):
        data = {'email': 'test1@gmail.com',
                'name': 'test1',
                'about_me': 'test',
                'favourite_music': 'test',
                'favourite_books': 'test',
                'favourite_movies': 'test',
                'gender': True,
                'city': 'Trent',
                'following': ''}
        form = EditUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_change_password_form_valid(self):
        data = {'password': 'test_pass',
                'confirm_password': 'test_pass'}
        form = ChangePasswordForm(data=data)
        self.assertTrue(form.is_valid())

    def test_change_password_form_invalid(self):
        prev_pass = self.user.password
        data = {'password': 'test_pass',
                'confirm_password': 'test_pas'}
        form = ChangePasswordForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(self.user.password, prev_pass)
