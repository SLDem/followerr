from django.test import TestCase, Client
from django.utils.encoding import force_bytes
from django.urls import reverse

from .forms import NewPostForm

from .models import Post
from user_profile.models import User
from comments.models import Comment

from django.test import tag


class PostModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        Post.objects.create(user=user, body='hi')
        self.post = Post.objects.get(body='hi')
        self.user = User.objects.get(email='test@gmail.com')
        self.client.login(email=user.email, password=user.password)

    def test_post_creation(self):
        self.assertTrue(isinstance(self.post, Post))
        self.assertEqual(self.post.__unicode__(), self.post.body)

    def test_post_deletion(self):
        self.post.delete()
        self.assertEqual(len(Post.objects.filter(body='hi')), 0)

    def test_post_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertEqual(url, '/post_detail/1/')


class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        self.user1 = User.objects.create_user(email='test1@gmail.com', password='test1', name='test1')

        self.post = Post.objects.create(user=self.user, body='hi')
        self.post1 = Post.objects.create(user=self.user, body='hi hello')
        self.post2 = Post.objects.create(user=self.user, body='hello hello')

        self.client.force_login(self.user)

    def test_index(self):
        response = self.client.get('/home/', {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('index.html')

    def test_index_logged_out(self):
        self.client.logout()
        response = self.client.get('/home/', {}, True)
        self.assertRedirects(response, reverse('login'))

    def test_index_add_post(self):
        self.client.post(reverse('index'), data={'body': 'Test'}, follow=True)
        self.assertEqual(len(Post.objects.filter(body='Test')), 1)

    def test_index_search(self):
        response = self.client.get('/?q=hi')
        self.assertIn(force_bytes('hi'), response.content)
        self.assertIn(force_bytes('hi hello'), response.content)

    def test_post_detail(self):
        response = self.client.get('/post_detail/{0}/'.format(self.post.pk), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(force_bytes(self.post.body), response.content)

    def test_post_detail_logged_out(self):
        self.client.logout()
        response = self.client.get('/post_detail/{0}/'.format(self.post.pk), follow=True)
        self.assertRedirects(response, reverse('login'))

    def test_post_detail_post_comment(self):
        data = {'body': 'test_comment'}
        self.client.post(reverse('post_detail', kwargs={'pk': self.post.pk}), data=data)
        self.assertEqual(len(Comment.objects.filter(body='test_comment')), 1)

    def test_post_detail_post_doesnt_exist(self):
        response = self.client.get(reverse('post_detail', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Post does not exist'), response.content)

    def test_edit_post(self):
        response = self.client.get(reverse('edit_post', kwargs={'pk': self.post.pk}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_post_request(self):
        data = {'body': 'test_edit'}
        self.client.post(reverse('edit_post', kwargs={'pk': self.post.pk}), data=data, follow=True)
        self.assertEqual(len(Post.objects.filter(body='test_edit')), 1)

    def test_edit_post_logged_out(self):
        self.client.logout()
        response = self.client.get(reverse('edit_post', kwargs={'pk': self.post.pk}))
        self.assertRedirects(response, reverse('login'))

    def test_edit_post_not_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('edit_post', kwargs={'pk': self.post.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_edit_post_doesnt_exist(self):
        response = self.client.get(reverse('edit_post', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Post does not exist'), response.content)

    def test_post_edit_fail(self):
        response = self.client.get('/edit_post/{0}/'.format('10'), follow=True)
        self.assertIn(force_bytes('Post does not exist'), response.content)

    def test_like_post(self):
        self.client.get(reverse('like_post', kwargs={'pk': self.post.pk}))
        self.assertIn(self.user, self.post.likers.all())

        self.client.get(reverse('like_post', kwargs={'pk': self.post.pk}))
        self.assertNotIn(self.user, self.post.likers.all())
        self.assertNotIn(self.user, self.post.dislikers.all())

        self.client.get(reverse('like_post', kwargs={'pk': self.post.pk}))
        self.assertIn(self.user, self.post.likers.all())
        self.assertNotIn(self.user, self.post.dislikers.all())

        self.post.dislikers.add(self.user)
        self.post.likers.remove(self.user)
        self.client.get(reverse('like_post', kwargs={'pk': self.post.pk}))
        self.assertIn(self.user, self.post.likers.all())
        self.assertNotIn(self.user, self.post.dislikers.all())

    def test_like_post_fail(self):
        response = self.client.get(reverse('like_post', kwargs={'pk': '10'}))
        self.assertIn(force_bytes('Post does not exist'), response.content)

    def test_dislike_post(self):
        self.client.get(reverse('dislike_post', kwargs={'pk': self.post.pk}))
        self.assertIn(self.user, self.post.dislikers.all())

        self.client.get(reverse('dislike_post', kwargs={'pk': self.post.pk}))
        self.assertNotIn(self.user, self.post.dislikers.all())
        self.assertNotIn(self.user, self.post.likers.all())

        self.client.get(reverse('dislike_post', kwargs={'pk': self.post.pk}))
        self.assertIn(self.user, self.post.dislikers.all())
        self.assertNotIn(self.user, self.post.likers.all())

        self.post.likers.add(self.user)
        self.post.dislikers.remove(self.user)
        self.client.get(reverse('dislike_post', kwargs={'pk': self.post.pk}))
        self.assertIn(self.user, self.post.dislikers.all())
        self.assertNotIn(self.user, self.post.likers.all())

    def test_dislike_post_fail(self):
        response = self.client.get(reverse('dislike_post', kwargs={'pk': '10'}))
        self.assertIn(force_bytes('Post does not exist'), response.content)

    def test_delete_post(self):
        self.client.get(reverse('delete_post', kwargs={'pk': self.post.pk}), follow=True)
        self.assertEqual(len(Post.objects.filter(body='hi')), 0)

    def test_delete_post_not_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('delete_post', kwargs={'pk': self.post.pk}), follow=True)
        self.assertIn(force_bytes('You can only delete your own posts'), response.content)

    def test_delete_post_doesnt_exist(self):
        response = self.client.get(reverse('delete_post', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Post does not exist'), response.content)

class PostFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', password='test')

    def test_new_post_form_valid(self):
        p = Post.objects.create(user=self.user, body='hi')
        data = {'body': p.body}
        form = NewPostForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_post_form_invalid(self):
        p = Post.objects.create(user=self.user, body='')
        data = {'body': p.body}
        form = NewPostForm(data=data)
        self.assertFalse(form.is_valid())
